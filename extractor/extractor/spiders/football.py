import json
import logging

import scrapy
from ..items import MatchItem


class FootballSpider(scrapy.Spider):
    name = 'football'
    allowed_domains = ['fff.fr']
    start_urls = ['http://districtfoot85.fff.fr/competitions']

    def parse(self, response):
        
        # recovery of data of the various championships
        data_json_string = response.css('#championnat-data::text').get()  # TODO: même chose avec #coupe-data
        championships = json.loads(data_json_string)


        for championship in championships:
            championship_id = championship.get('id')
            championship_name = championship.get('name')
            if championship_id is None or championship_name is None:
                logging.warning(championship)
            for stage in championship['stages']:
                stage_id = stage['number']
                for group in stage['groups']:
                    group_id = group['number']
                    yield scrapy.Request(
                        f'https://districtfoot85.fff.fr/competitions/?id={championship_id}&poule={group_id}&phase={stage_id}&type=ch&tab=calendar',
                        self.parse_calendar
                    )

    def parse_calendar(self, response):
        # scrapy.shell.inspect_response(response, self)
        championship_name = response.css('h1::text').get()

        # TODO: les 2 champs suivants sont extraits en majuscules
        phase_name = response.xpath('//select[@id=$id_]/option[@selected]/text()', id_="phase-competition").get()
        group_name = response.xpath('//select[@id=$id_]/option[@selected]/text()', id_="poule-competition").get()

        journeys = response.css('#calendrier-tab .results-content')
        for journey in journeys:
            confrontations = journey.css('.result-display > a::attr(href)').getall()
            for confrontation in confrontations:
                yield scrapy.Request(
                    response.urljoin(confrontation),
                    self.parse_confrontation
                )

    def parse_confrontation(self, response):
        # TODO: le match a-t-il été joué ?

        journey = response.css('span.day::text').get().strip()
        championship_name = response.css('span.ch-type::text').get()

        # TODO: récupérer les noms d'équipes sur la page précédente (calendrier), pck + précis
        team_a = response.css('.team1::text').get()  # TODO: en majuscule
        team_b = response.css('.team2::text').get()

        team_links = response.css('.team > a::attr(href)').getall()
        team_a_link, team_b_link = team_links

        team_logos = response.css('.team img::attr(src)').getall()
        team_a_logo, team_b_logo = team_logos

        # Raw date extracted as "dimanche 20 février 2022 - 13H00", must be clean in a pipeline
        confrontation_date = response.css('.date-ch::text').get().strip()

        # TODO: sources d'erreurs possible
        pitch_info = response.css('.infos-grounds > p::text').getall()
        pitch_name = pitch_info[0].strip()
        pitch_type = pitch_info[-1].strip()

        # string html, devra être splittée (" - ") puis nettoyée dans un pipeline
        score = response.css('span.result-numbers').get()

        item = MatchItem()
        item['score'] = score
        item['team_a'] = team_a
        item['team_b'] = team_b
        item['journey'] = journey
        item['pitch_name'] = pitch_name
        item['pitch_type'] = pitch_type
        item['team_a_link'] = team_a_link
        item['team_b_link'] = team_b_link
        item['team_a_logo'] = team_a_logo
        item['team_b_logo'] = team_b_logo
        item['championship_name'] = championship_name
        item['confrontation_date'] = confrontation_date
        return item


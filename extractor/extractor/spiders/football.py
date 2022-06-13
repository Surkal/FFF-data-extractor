import json
import logging

import scrapy
from ..items import MatchItem


class FootballSpider(scrapy.Spider):
    name = 'football'
    allowed_domains = ['fff.fr']
    start_urls = ['https://www.fff.fr/competition']

    def parse(self, response):
        subdomains = response.css('#coordonnees a::attr(href)').getall()
        for subdomain in subdomains:
            # on the FFF's website, only one subdomain (lfpl) has this redirection error
            if not 'competition' in subdomain:
                subdomain = response.urljoin('/competitions')
            
            yield scrapy.Request(subdomain, self.parse_subdomain)

    def parse_subdomain(self, response):
        
        # recovery of data of the various championships
        data_json_string = response.css('#championnat-data::text').get()
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
                        response.urljoin(f'?id={championship_id}&poule={group_id}&phase={stage_id}&type=ch&tab=calendar'),
                        self.parse_calendar
                    )

        data_json_string = response.css('#coupe-data::text').get()
        cups = json.loads(data_json_string)
        for cup in cups:
            cup_id = cup.get('id')
            cup_name = cup.get('name')
            for stage in cup['stages']:
                for group in stage['groups']:
                    group_id = group['number']
                    yield scrapy.Request(
                            response.urljoin(f'?id={cup_id}&poule={group_id}&type=ch&tab=resultat'),
                            self.parse_cup_calendar
                        )

    def parse_cup_calendar(self, response):
        championship_name = response.css('h1::text').get()

        confrontations = response.css('#agenda .results-content')
        for confrontation in confrontations:
            if not confrontation.css('.equipe1'):
                # ignore empty (useless) div
                continue
            team_a_name = confrontation.css('.equipe1 .name::text').get().strip()
            team_b_name = confrontation.css('.equipe2 .name::text').get().strip()
            confrontation_url = confrontation.css('a::attr(href)').get()

            request = scrapy.Request(
                    response.urljoin(confrontation_url),
                    self.parse_confrontation
                )
            request.meta['data'] = {
                'team_a_name': team_a_name,
                'team_b_name': team_b_name,
            }
            yield request

        # let's visit the previous turn
        previous_turn = response.css('#agenda a::attr(href)').get()
        yield scrapy.Request(
            response.urljoin(previous_turn),
            self.parse_cup_calendar
        )

    def parse_calendar(self, response):
        championship_name = response.css('h1::text').get()

        # TODO: les 2 champs suivants sont extraits en majuscules
        phase_name = response.xpath('//select[@id=$id_]/option[@selected]/text()', id_="phase-competition").get()
        group_name = response.xpath('//select[@id=$id_]/option[@selected]/text()', id_="poule-competition").get()

        journeys = response.css('#calendrier-tab .results-content')
        for journey in journeys:
            confrontations = journey.css('.result-display')
            for confrontation in confrontations:
                if not confrontation.css('.equipe1'):
                    # ignore empty (useless) div
                    continue
                team_a_name = confrontation.css('.equipe1 .name::text').get().strip()
                team_b_name = confrontation.css('.equipe2 .name::text').get().strip()
                confrontation_url = confrontation.css('a::attr(href)').get()

                request = scrapy.Request(
                    response.urljoin(confrontation_url),
                    self.parse_confrontation
                )
                request.meta['data'] = {
                    'team_a_name': team_a_name,
                    'team_b_name': team_b_name,
                    'phase_name': phase_name,
                    'group_name': group_name,
                }
                yield request

    def parse_confrontation(self, response):
        # scrapy.shell.inspect_response(response, self)
        data = response.meta.get('data')

        # was there a penalty session ?
        team_a_pen = response.css('.fullresults').get()

        journey = response.css('span.day::text').get().strip()
        championship_name = response.css('span.ch-type::text').get()

        # TODO: récupérer les noms d'équipes sur la page précédente (calendrier), pck + précis
        team_a = response.css('.team1::text').get()  # TODO: en majuscule
        team_b = response.css('.team2::text').get()

        team_links = response.css('.team > a::attr(href)').getall()
        team_a_link, team_b_link = team_links

        team_logos = response.css('.team img::attr(src)').getall()
        team_a_logo, team_b_logo = team_logos

        team_a_has_withdrawn = not not response.css('.team-logo1 .forfait::text').get().strip()
        team_b_has_withdrawn = not not response.css('.team-logo2 .forfait::text').get().strip()

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
        item['phase_name'] = data.get('phase_name')
        item['group_name'] = data.get('group_name')
        item['pitch_name'] = pitch_name
        item['pitch_type'] = pitch_type
        item['team_a_link'] = team_a_link
        item['team_b_link'] = team_b_link
        item['team_a_logo'] = team_a_logo
        item['team_b_logo'] = team_b_logo
        item['team_a_name'] = data['team_a_name']
        item['team_b_name'] = data['team_b_name']
        item['championship_name'] = championship_name
        item['confrontation_url'] = response.url
        item['confrontation_date'] = confrontation_date
        item['team_a_has_withdrawn'] = team_a_has_withdrawn
        item['team_b_has_withdrawn'] = team_b_has_withdrawn
        item['team_a_pen'] = team_a_pen
        return item

    
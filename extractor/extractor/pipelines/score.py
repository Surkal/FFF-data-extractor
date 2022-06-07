import re

import requests
from scrapy.exceptions import DropItem


class ScorePipeline:
    def process_item(self, item, spider):
        scores = item['score'].split(' - ')
        if len(scores) != 2:
            raise DropItem("Missing score")
        item['score_team_a'] = self.get_team_score(scores[0])
        item['score_team_b'] = self.get_team_score(scores[1])
        del item['score']
        return item

    def get_team_score(self, html_string):
        images = self.get_src_from_img(html_string)
        score = ''
        for image in images:
            score += self.get_number(image)
        return int(score)

    def get_src_from_img(self, html_string):
        pattern = r"src=\"([^\"]+)"
        return re.findall(pattern, html_string)

    def get_number(self, url):
        numbers = [2543, 733, 1921, 1987, 1595, 1909, 2632, 1276, 2585, 2570]
        response = requests.get(url)
        content_size = len(response.content)
        if content_size not in numbers:
            raise DropItem("Score not recognizable")
        return str(numbers.index(content_size))
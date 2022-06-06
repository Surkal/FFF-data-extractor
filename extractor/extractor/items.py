import scrapy


class MatchItem(scrapy.Item):
    score = scrapy.Field()
    team_a = scrapy.Field()
    team_b = scrapy.Field()
    journey = scrapy.Field()
    pitch_name = scrapy.Field()
    pitch_type = scrapy.Field()
    team_a_link = scrapy.Field()
    team_b_link = scrapy.Field()
    team_a_logo = scrapy.Field()
    team_b_logo = scrapy.Field()
    score_team_a = scrapy.Field()
    score_team_b = scrapy.Field()
    championship_name = scrapy.Field()
    confrontation_date = scrapy.Field()

import scrapy


class MatchItem(scrapy.Item):
    # Team information
    team_a = scrapy.Field()
    team_b = scrapy.Field()
    team_a_name = scrapy.Field()
    team_b_name = scrapy.Field()
    team_a_link = scrapy.Field()
    team_b_link = scrapy.Field()
    team_a_logo = scrapy.Field()
    team_b_logo = scrapy.Field()

    # Place information
    journey = scrapy.Field()
    phase_name = scrapy.Field()
    group_name = scrapy.Field()
    pitch_name = scrapy.Field()
    pitch_type = scrapy.Field()
    championship_name = scrapy.Field()
    confrontation_url = scrapy.Field()
    confrontation_date = scrapy.Field()  # A Datetime object

    # Score
    score = scrapy.Field()
    team_a_has_withdrawn = scrapy.Field()
    team_b_has_withdrawn = scrapy.Field()

    # number of goals scored by each team
    score_team_a = scrapy.Field()
    score_team_b = scrapy.Field()

    # number of penalties scored by each team at the end of a playoff game
    team_a_pen = scrapy.Field()
    team_b_pen = scrapy.Field()
    
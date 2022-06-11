from scrapy.exceptions import DropItem


class MatchPipeline:
    """
    When one of the two teams is called "Exempt",
    it meansthat the other team is off.
    """
    def process_item(self, item, spider):
        if (item['team_a'] == 'Exempt' or item['team_b'] == 'Exempt'):
            DropItem(f'Not a real match : {item["url"]}')
        return item
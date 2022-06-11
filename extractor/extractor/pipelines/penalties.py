import re


class PenaltiesPipeline:
    def process_item(self, item, spider):
        team_a_pen, team_b_pen = self.get_results(item['team_a_pen'])
        if team_a_pen is None:
            del item['team_a_pen']
        else:
            item['team_a_pen'] = team_a_pen
            item['team_b_pen'] = team_b_pen
        return item

    def get_results(self, raw_string):
        pattern = r"TAB\s+(\d+)\s+-\s+(\d+)"
        match = re.search(pattern, raw_string)
        if match is None:
            return None, None
        return int(match.group(1)), int(match.group(2))
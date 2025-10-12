"""
Example usage of the AI Summary endpoint
"""

import requests
import json
from typing import Dict, Any


class SurveyAnalyzer:
    """Client for interacting with the Survey AI Summary API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def get_ai_summary(self, survey_uuid: str) -> Dict[str, Any]:
        """
        Get AI-generated summary for a survey
        
        Args:
            survey_uuid: UUID of the survey
            
        Returns:
            Dictionary containing the summary data
        """
        url = f"{self.base_url}/api/surveys/{survey_uuid}/ai-summary"
        
        try:
            response = requests.get(url, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching AI summary: {e}")
            return None
    
    def get_basic_stats(self, survey_uuid: str) -> Dict[str, Any]:
        """Get basic survey statistics"""
        url = f"{self.base_url}/api/surveys/{survey_uuid}/stats"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def print_summary_report(self, survey_uuid: str):
        """Print a formatted report of the AI summary"""
        data = self.get_ai_summary(survey_uuid)
        
        if not data or not data.get('success'):
            print("Failed to get AI summary")
            return
        
        summary = data['data']['summary']
        
        print("\n" + "="*60)
        print(f"AI SURVEY SUMMARY REPORT")
        print(f"Survey: {data['data']['survey_title']}")
        print(f"Company: {data['data']['company']}")
        print("="*60)
        
        print(f"\n📊 PARTICIPATION METRICS")
        print(f"Total Participants: {summary['total_participants']}")
        print(f"Completed: {summary['completed_surveys']}")
        print(f"In Progress: {summary['in_progress_surveys']}")
        print(f"Completion Rate: {summary['completion_rate_percentage']}%")
        
        print(f"\n😊 SENTIMENT")
        print(f"Positive Indicators: {summary['positive_indicators']}")
        print(f"Negative Indicators: {summary['negative_indicators']}")
        
        print(f"\n🔑 TOP KEYWORDS")
        for i, keyword in enumerate(summary['top_keywords'], 1):
            print(f"  {i}. {keyword}")
        
        print(f"\n⚠️  KEY PAIN POINTS")
        for i, pain_point in enumerate(summary['key_pain_points'], 1):
            print(f"  {i}. {pain_point}")
        
        print(f"\n🔄 COMMON WORKFLOWS")
        for i, workflow in enumerate(summary['common_workflows'], 1):
            print(f"  {i}. {workflow}")
        
        print(f"\n🚀 TECHNOLOGY TRENDS")
        for i, trend in enumerate(summary['technology_trends'], 1):
            print(f"  {i}. {trend}")
        
        print(f"\n🛑 MAIN BOTTLENECKS")
        for i, bottleneck in enumerate(summary['main_bottlenecks'], 1):
            print(f"  {i}. {bottleneck}")
        
        print(f"\n💰 BUDGET INSIGHTS")
        print(f"  {summary['budget_insights']}")
        
        print(f"\n🔒 SECURITY CONCERNS")
        for i, concern in enumerate(summary['security_concerns'], 1):
            print(f"  {i}. {concern}")
        
        print(f"\n☁️  DEPLOYMENT PREFERENCES")
        for i, pref in enumerate(summary['deployment_preferences'], 1):
            print(f"  {i}. {pref}")
        
        print(f"\n💡 KEY INSIGHTS")
        print(f"  {summary['key_insights']}")
        
        print(f"\n✅ RECOMMENDATIONS")
        print(f"  {summary['recommendations']}")
        
        print("\n" + "="*60 + "\n")
    
    def export_to_json(self, survey_uuid: str, filename: str = None):
        """Export summary to JSON file"""
        if filename is None:
            filename = f"survey_summary_{survey_uuid}.json"
        
        data = self.get_ai_summary(survey_uuid)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Summary exported to {filename}")
    
    def compare_surveys(self, survey_uuids: list):
        """Compare multiple surveys side by side"""
        summaries = []
        
        for uuid in survey_uuids:
            data = self.get_ai_summary(uuid)
            if data and data.get('success'):
                summaries.append({
                    'uuid': uuid,
                    'title': data['data']['survey_title'],
                    'summary': data['data']['summary']
                })
        
        print("\n" + "="*80)
        print("SURVEY COMPARISON")
        print("="*80)
        
        # Compare participation
        print("\n📊 PARTICIPATION COMPARISON")
        print(f"{'Survey':<30} {'Participants':<15} {'Completed':<15} {'Rate':<10}")
        print("-" * 80)
        for s in summaries:
            print(f"{s['title'][:28]:<30} "
                  f"{s['summary']['total_participants']:<15} "
                  f"{s['summary']['completed_surveys']:<15} "
                  f"{s['summary']['completion_rate_percentage']:.1f}%")
        
        # Compare top pain points
        print("\n⚠️  TOP PAIN POINTS ACROSS SURVEYS")
        all_pain_points = {}
        for s in summaries:
            for pain in s['summary']['key_pain_points']:
                all_pain_points[pain] = all_pain_points.get(pain, 0) + 1
        
        sorted_pains = sorted(all_pain_points.items(), key=lambda x: x[1], reverse=True)
        for pain, count in sorted_pains[:10]:
            print(f"  [{count}] {pain}")
        
        print("\n" + "="*80 + "\n")


# Example usage
if __name__ == "__main__":
    analyzer = SurveyAnalyzer()
    
    # Example 1: Print summary for a single survey
    print("Example 1: Single Survey Analysis")
    survey_uuid = "your-survey-uuid-here"
    analyzer.print_summary_report(survey_uuid)
    
    # Example 2: Export to JSON
    print("\nExample 2: Export Summary")
    analyzer.export_to_json(survey_uuid)
    
    # Example 3: Compare multiple surveys
    print("\nExample 3: Compare Surveys")
    survey_ids = [
        "survey-uuid-1",
        "survey-uuid-2",
        "survey-uuid-3"
    ]
    # analyzer.compare_surveys(survey_ids)
    
    # Example 4: Extract specific metrics
    print("\nExample 4: Extract Specific Metrics")
    data = analyzer.get_ai_summary(survey_uuid)
    if data and data.get('success'):
        summary = data['data']['summary']
        
        print(f"\nQuick Metrics:")
        print(f"- Completion Rate: {summary['completion_rate_percentage']}%")
        print(f"- Top Keyword: {summary['top_keywords'][0] if summary['top_keywords'] else 'N/A'}")
        print(f"- #1 Pain Point: {summary['key_pain_points'][0] if summary['key_pain_points'] else 'N/A'}")
        print(f"- Positive/Negative Ratio: {summary['positive_indicators']}/{summary['negative_indicators']}")


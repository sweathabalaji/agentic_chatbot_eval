"""
Run evaluation tests on the Mutual Funds Agent
"""

import asyncio
import argparse
from typing import List, Dict, Any
from tabulate import tabulate

from evaluation.agent_wrapper import get_evaluated_agent
from database.db import get_eval_db
from utils.logger import get_logger

logger = get_logger(__name__)


class EvaluationRunner:
    """Runs evaluation tests and generates reports"""
    
    def __init__(self):
        self.agent = get_evaluated_agent()
        self.db = get_eval_db()
        
    async def run_test_suite(self, category: str = None) -> Dict[str, Any]:
        """Run all test cases from database"""
        
        logger.info(f"🧪 Loading test cases (category: {category or 'ALL'})")
        test_cases = self.db.get_test_cases(category)
        
        if not test_cases:
            logger.warning("No test cases found in database")
            return {'total': 0, 'results': []}
        
        logger.info(f"Found {len(test_cases)} test cases")
        
        results = []
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"Test Case {i}/{len(test_cases)}")
            logger.info(f"Query: {test_case['test_query']}")
            logger.info(f"Expected Intent: {test_case['expected_intent']}")
            logger.info(f"Category: {test_case['category']}")
            logger.info(f"{'='*80}")
            
            # Run through evaluated agent
            result = await self.agent.process_request_with_evaluation(
                user_prompt=test_case['test_query'],
                expected_intent=test_case['expected_intent']
            )
            
            # Extract key metrics
            eval_data = result.get('evaluation', {})
            
            test_result = {
                'test_id': test_case['id'],
                'query': test_case['test_query'],
                'expected_intent': test_case['expected_intent'],
                'predicted_intent': eval_data.get('intent_predicted'),
                'intent_match': eval_data.get('intent_match'),
                'confidence': eval_data.get('intent_confidence', 0),
                'passed_threshold': eval_data.get('passed_threshold'),
                'relevance': eval_data.get('relevance_score'),
                'hallucination': eval_data.get('hallucination_score'),
                'faithfulness': eval_data.get('faithfulness_score'),
                'latency_ms': result.get('latency_ms'),
                'category': test_case['category'],
                'difficulty': test_case['difficulty']
            }
            
            results.append(test_result)
            
            # Print result summary
            logger.info(f"\n📊 Results:")
            logger.info(f"  Intent Match: {'✅' if test_result['intent_match'] else '❌'}")
            logger.info(f"  Confidence: {test_result['confidence']:.2f}")
            logger.info(f"  Passed Threshold: {'✅' if test_result['passed_threshold'] else '❌'}")
            logger.info(f"  Relevance: {test_result['relevance']:.2f}" if test_result['relevance'] else "  Relevance: N/A")
            logger.info(f"  Latency: {test_result['latency_ms']}ms")
        
        return self._generate_summary(results)
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from test results"""
        
        total = len(results)
        intent_matches = sum(1 for r in results if r.get('intent_match'))
        passed_threshold = sum(1 for r in results if r.get('passed_threshold'))
        
        # Calculate averages (filter None values)
        relevances = [r['relevance'] for r in results if r.get('relevance') is not None]
        hallucinations = [r['hallucination'] for r in results if r.get('hallucination') is not None]
        latencies = [r['latency_ms'] for r in results if r.get('latency_ms') is not None]
        
        summary = {
            'total': total,
            'intent_accuracy': intent_matches / total if total > 0 else 0,
            'threshold_pass_rate': passed_threshold / total if total > 0 else 0,
            'avg_relevance': sum(relevances) / len(relevances) if relevances else None,
            'avg_hallucination': sum(hallucinations) / len(hallucinations) if hallucinations else None,
            'avg_latency_ms': sum(latencies) / len(latencies) if latencies else None,
            'results': results
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print formatted summary table"""
        
        print("\n" + "="*100)
        print("📊 EVALUATION SUMMARY")
        print("="*100)
        
        # Overall metrics
        print(f"\n🎯 Overall Performance:")
        print(f"  Total Test Cases: {summary['total']}")
        print(f"  Intent Accuracy: {summary['intent_accuracy']:.1%}")
        print(f"  Threshold Pass Rate: {summary['threshold_pass_rate']:.1%}")
        
        if summary['avg_relevance']:
            print(f"  Average Relevance: {summary['avg_relevance']:.3f}")
        if summary['avg_hallucination']:
            print(f"  Average Hallucination: {summary['avg_hallucination']:.3f}")
        if summary['avg_latency_ms']:
            print(f"  Average Latency: {summary['avg_latency_ms']:.0f}ms")
        
        # Results by category
        results = summary['results']
        categories = {}
        for r in results:
            cat = r['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)
        
        print(f"\n📋 Results by Category:")
        for cat, cat_results in categories.items():
            matches = sum(1 for r in cat_results if r.get('intent_match'))
            print(f"  {cat}: {matches}/{len(cat_results)} correct ({matches/len(cat_results):.1%})")
        
        # Detailed results table
        print(f"\n📝 Detailed Results:")
        table_data = []
        for r in results:
            table_data.append([
                r['query'][:50] + '...' if len(r['query']) > 50 else r['query'],
                r['expected_intent'],
                r['predicted_intent'],
                '✅' if r.get('intent_match') else '❌',
                f"{r['confidence']:.2f}",
                f"{r['relevance']:.2f}" if r.get('relevance') else 'N/A',
                f"{r['latency_ms']}ms"
            ])
        
        headers = ['Query', 'Expected', 'Predicted', 'Match', 'Conf', 'Rel', 'Latency']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        print("\n" + "="*100)
    
    def get_performance_report(self, days: int = 7):
        """Generate performance report from stored evaluations"""
        
        print(f"\n📈 Performance Report (Last {days} Days)")
        print("="*80)
        
        summary = self.agent.get_performance_summary(days)
        
        if not summary:
            print("No data available")
            return
        
        overall = summary.get('summary', {})
        print(f"\n📊 Overall Metrics:")
        print(f"  Total Queries: {overall.get('total_queries', 0)}")
        print(f"  Average Relevance: {overall.get('avg_relevance', 0):.3f}")
        print(f"  Average Hallucination: {overall.get('avg_hallucination', 0):.3f}")
        print(f"  Average Latency: {overall.get('avg_latency', 0):.0f}ms")
        print(f"  Pass Rate: {overall.get('pass_rate', 0):.1%}")
        print(f"  Error Rate: {overall.get('error_rate', 0):.1%}")
        
        by_intent = summary.get('by_intent', [])
        if by_intent:
            print(f"\n📋 Top Intents:")
            for intent_data in by_intent[:5]:
                print(f"  {intent_data['intent_predicted']}: {intent_data['intent_count']} queries")
        
        print("="*80)


async def main():
    parser = argparse.ArgumentParser(description='Run MF Agent Evaluation Tests')
    parser.add_argument('--category', type=str, help='Filter by category')
    parser.add_argument('--report', action='store_true', help='Show performance report')
    parser.add_argument('--days', type=int, default=7, help='Days for report')
    
    args = parser.parse_args()
    
    runner = EvaluationRunner()
    
    if args.report:
        runner.get_performance_report(args.days)
    else:
        summary = await runner.run_test_suite(args.category)
        runner.print_summary(summary)


if __name__ == '__main__':
    asyncio.run(main())

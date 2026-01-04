#!/usr/bin/env python3
"""
Extract and summarize activity data by month from timeline.csv
"""

import csv
from collections import defaultdict


def parse_timeline_by_month(csv_file):
    """Parse timeline.csv and group activities by month"""
    
    monthly_data = defaultdict(lambda: {
        'activities': [],
        'total_distance': 0.0,
        'total_duration': 0.0,
        'activity_counts': defaultdict(int),
        'visit_counts': 0
    })
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Extract year-month from timestamp (first 7 chars: YYYY-MM)
            timestamp = row['timestamp']
            month = timestamp[:7]  # "2025-06"
            
            record_type = row['record_type']
            
            # Add to monthly data
            monthly_data[month]['activities'].append(row)
            
            # Sum distances and durations
            distance = float(row['distance_meters']) if row['distance_meters'] else 0.0
            duration = float(row['duration_seconds']) if row['duration_seconds'] else 0.0
            
            monthly_data[month]['total_distance'] += distance
            monthly_data[month]['total_duration'] += duration
            
            # Count activity types
            if record_type == 'activity':
                activity_type = row['activity_type']
                monthly_data[month]['activity_counts'][activity_type] += 1
            elif record_type == 'visit':
                monthly_data[month]['visit_counts'] += 1
    
    return monthly_data

def print_monthly_summary(monthly_data, output_file=None):
    """Print summary of activities by month"""
    
    output_lines = []
    
    # Sort months chronologically
    for month in sorted(monthly_data.keys()):
        data = monthly_data[month]
        
        lines = [
            f"\n{'='*60}",
            f"MONTH: {month}",
            f"{'='*60}",
            f"Total Activities: {len(data['activities'])}",
            f"Total Distance: {data['total_distance']/1000:.2f} km",
            f"Total Duration: {data['total_duration']/3600:.2f} hours",
            f"Visits: {data['visit_counts']}",
            f"\nActivity Breakdown:"
        ]
        
        for activity_type, count in sorted(data['activity_counts'].items()):
            lines.append(f"  - {activity_type}: {count}")
        
        output_lines.extend(lines)
        
        # Print to console
        for line in lines:
            print(line)
    
    # Optionally save to file
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        print(f"\n\nSummary saved to {output_file}")

def print_detailed_monthly_activities(monthly_data, month, output_file=None):
    """Print detailed activity list for a specific month"""
    
    if month not in monthly_data:
        print(f"No data found for month: {month}")
        return
    
    data = monthly_data[month]
    output_lines = []
    
    lines = [
        f"\n{'='*80}",
        f"DETAILED ACTIVITIES FOR {month}",
        f"{'='*80}\n"
    ]
    
    for i, activity in enumerate(data['activities'], 1):
        distance_km = float(activity['distance_meters'])/1000 if activity['distance_meters'] else 0
        duration_min = float(activity['duration_seconds'])/60 if activity['duration_seconds'] else 0
        
        activity_lines = [
            f"{i}. {activity['timestamp']} - {activity['end_timestamp']}",
            f"   Type: {activity['record_type']} | {activity['activity_type']}",
            f"   Distance: {distance_km:.2f} km | Duration: {duration_min:.1f} min",
            ""
        ]
        lines.extend(activity_lines)
    
    output_lines.extend(lines)
    
    # Print to console
    for line in lines:
        print(line)
    
    # Optionally save to file
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        print(f"\nDetailed activities saved to {output_file}")

if __name__ == "__main__":
    import sys
    
    csv_file = "timeline.csv"
    
    # Parse the timeline
    print(f"Reading {csv_file}...")
    monthly_data = parse_timeline_by_month(csv_file)
    
    # Print summary for all months
    print_monthly_summary(monthly_data)
    
    # Optional: Save summary to file
    print_monthly_summary(monthly_data, output_file="monthly-summary.txt")
    
    # Optional: Print detailed activities for a specific month
    # Uncomment and modify the month as needed:
    # print_detailed_monthly_activities(monthly_data, "2025-06", output_file="2025-06_details.txt")

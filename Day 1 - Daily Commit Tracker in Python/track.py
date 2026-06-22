# 🌟 Daily Commit Tracker - Day 1 (Complete English Version)
# 100 Days of Code Challenge
# Author: Aliza Javed

import datetime
import json
import os
import random

def load_progress():
    """Load previous progress from a JSON file"""
    try:
        with open('progress.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"days": [], "current_streak": 0}

def save_progress(data):
    """Save progress to JSON file"""
    with open('progress.json', 'w') as f:
        json.dump(data, f, indent=2)

def view_progress():
    """Display all previous entries"""
    progress = load_progress()
    if not progress["days"]:
        print("\n📭 No progress recorded yet!")
        return
    
    print("\n📊 YOUR PROGRESS HISTORY")
    print("=" * 50)
    for day in progress["days"]:
        print(f"Day {day['day']}: {day['project']} ({day['date']})")
        print(f"   Goal: {day['goal']}")
        print(f"   Language: {day['language']}")
        print("-" * 50)
    print(f"🔥 Current Streak: {progress['current_streak']} days")
    print("=" * 50)

def delete_last_entry():
    """Remove the last entry from progress"""
    progress = load_progress()
    if progress["days"]:
        removed = progress["days"].pop()
        progress["current_streak"] = len(progress["days"])
        save_progress(progress)
        print(f"\n🗑️ Removed Day {removed['day']}: {removed['project']}")
    else:
        print("\n📭 No entries to delete!")

def start_tracker():
    """Main function to log today's progress"""
    print("=" * 50)
    print("🌟 DAILY COMMIT TRACKER 🌟")
    print("=" * 50)
    
    # Load previous progress
    progress = load_progress()
    day_number = len(progress["days"]) + 1
    
    # Get user input (ALL IN ENGLISH)
    name = input("\n👤 Enter your name: ")
    goal = input("🎯 What is your goal for today? ")
    language = input("💻 Which language did you use? (Python/JS/etc): ")
    project_name = input("📁 What is your project name? ")
    
    today = datetime.date.today()
    
    # Save today's entry
    entry = {
        "day": day_number,
        "date": str(today),
        "project": project_name,
        "goal": goal,
        "language": language,
        "completed": True
    }
    progress["days"].append(entry)
    progress["current_streak"] = day_number
    save_progress(progress)
    
    # Display summary (ALL IN ENGLISH)
    print("\n" + "=" * 50)
    print(f"📅 Date: {today}")
    print(f"🚀 Day: {day_number} of 100")
    print(f"👤 User: {name}")
    print(f"📁 Project: {project_name}")
    print(f"🎯 Goal: {goal}")
    print(f"💻 Language: {language}")
    print(f"🔥 Streak: {progress['current_streak']} days")
    print("=" * 50)
    
    print("\n✅ Today's Checklist:")
    print("   [✓] Wrote code")
    print("   [✓] Tested the code")
    print("   [✓] Made a Git commit")
    print("   [✓] Pushed to GitHub")
    print("   [✓] Saved progress")
    
    # Motivational messages (ALL IN ENGLISH)
    messages = [
        "💪 You're building a habit!",
        "🌟 Every expert was once a beginner!",
        "🚀 Consistency is the key to success!",
        "🎯 Focus on progress, not perfection!",
        "🔥 You're doing great! Keep going!",
        "💡 Small steps lead to big achievements!",
        "🌈 Keep pushing your limits!",
        "⭐ You're stronger than you think!"
    ]
    print(f"\n💬 {random.choice(messages)}")
    
    print(f"\n📊 Total days completed: {day_number}/100")
    print(f"🔥 Current streak: {progress['current_streak']} days")
    
    # Milestone celebrations
    if day_number == 1:
        print("\n🌟 Welcome to Day 1! Let's make it count! 🚀")
    elif day_number % 10 == 0:
        print(f"\n🎉 Congratulations on reaching Day {day_number}! 🎉")
    elif day_number % 25 == 0:
        print(f"\n🎊 Quarter milestone! {day_number} days done! 🎊")
    elif day_number % 50 == 0:
        print(f"\n🏆 Halfway there! {day_number} days completed! 🏆")
    
    print("\n" + "=" * 50)
    print("📝 Remember: Consistency beats perfection!")
    print("🙌 Keep showing up every day!")
    print("=" * 50)

def main_menu():
    """Display main menu with options"""
    while True:
        print("\n" + "=" * 50)
        print("📋 MAIN MENU")
        print("=" * 50)
        print("1. 📝 Log Today's Progress")
        print("2. 📊 View All Progress")
        print("3. 🗑️ Delete Last Entry")
        print("4. ❌ Exit")
        print("=" * 50)
        
        choice = input("Choose an option (1-4): ")
        
        if choice == "1":
            start_tracker()
        elif choice == "2":
            view_progress()
        elif choice == "3":
            delete_last_entry()
        elif choice == "4":
            print("\n👋 Goodbye! Keep coding! 🚀")
            break
        else:
            print("\n❌ Invalid choice! Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main_menu()
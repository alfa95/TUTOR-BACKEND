#!/usr/bin/env python3
"""
Test script for Supabase user topic progress integration
"""
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

def test_supabase_connection():
    """Test basic Supabase connection"""
    print("🧪 Testing Supabase Connection...")
    
    try:
        # Import after loading environment variables
        from src.db.supabase_utils import get_supabase_manager
        
        # Test basic connection by trying to access the client
        print("1. Testing connection...")
        manager = get_supabase_manager()
        client = manager.client
        print(f"   ✅ Connected successfully to Supabase!")
        
        print("\n🎉 Connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your .env file has SUPABASE_URL and SUPABASE_ANON_KEY")
        print("2. Verify your Supabase project is running")
        print("3. Check if your anon key has the right permissions")
        return False

def test_user_topic_progress():
    """Test GET operation on user_topic_progress table"""
    print("\n🧪 Testing User Topic Progress GET Operation...")
    
    try:
        from src.db.supabase_utils import get_user_topic_progress, get_user_topic_difficulty_progress, get_user_topic_summary
        
        test_user_id = "1d491e02-8489-4508-8196-d62553ab5e6a"
        
        print(f"🔍 Testing with user_id: {test_user_id}")
        
        # Test get user topic progress
        print("1. Testing get user topic progress...")
        progress_data = get_user_topic_progress(test_user_id)
        print(f"   ✅ Retrieved progress data: {len(progress_data)} entries")
        
        # Debug: Let's check what's in the table without filters
        print("\n2. Debug: Checking table contents...")
        try:
            from src.db.supabase_utils import get_supabase_manager
            manager = get_supabase_manager()
            
            # Check total rows in table
            all_data = manager.client.table('user_topic_progress').select('*').execute()
            print(f"   📊 Total rows in table: {len(all_data.data)}")
            
            if all_data.data:
                print("   📋 Sample data from table:")
                for i, row in enumerate(all_data.data[:3], 1):
                    print(f"      Row {i}: user_id={row.get('user_id')}, topic={row.get('topic')}, difficulty={row.get('difficulty')}")
            
            # Check if our user_id exists in any row
            user_exists = any(row.get('user_id') == test_user_id for row in all_data.data)
            print(f"   🔍 User ID '{test_user_id}' exists in table: {user_exists}")
            
            if not user_exists:
                print("   ⚠️  User ID not found. Available user_ids:")
                unique_users = set(row.get('user_id') for row in all_data.data if row.get('user_id'))
                for uid in list(unique_users)[:5]:  # Show first 5 unique user IDs
                    print(f"      - {uid}")
            
            # Test the exact query that should work
            print(f"\n3. Testing exact query for user_id: {test_user_id}")
            exact_query = manager.client.table('user_topic_progress').select('*').eq('user_id', test_user_id).execute()
            print(f"   📊 Exact query result count: {len(exact_query.data)}")
            
            if exact_query.data:
                print("   ✅ Exact query worked! Data found:")
                for row in exact_query.data:
                    print(f"      - {row}")
            else:
                print("   ❌ Exact query returned no results")
                
                # Let's try with different approaches
                print("\n4. Trying alternative approaches...")
                
                # Try with string comparison
                print("   a) Testing with string comparison...")
                string_query = manager.client.table('user_topic_progress').select('*').execute()
                matching_rows = [row for row in string_query.data if str(row.get('user_id')) == test_user_id]
                print(f"      String comparison found: {len(matching_rows)} rows")
                
                # Try with partial match
                print("   b) Testing with partial user_id match...")
                partial_match = [row for row in string_query.data if test_user_id in str(row.get('user_id'))]
                print(f"      Partial match found: {len(partial_match)} rows")
                
                # Check the exact data type
                print("   c) Checking data types...")
                if string_query.data:
                    sample_row = string_query.data[0]
                    user_id_type = type(sample_row.get('user_id'))
                    print(f"      user_id type in DB: {user_id_type}")
                    print(f"      test_user_id type: {type(test_user_id)}")
                    print(f"      Are they equal? {sample_row.get('user_id') == test_user_id}")
            
            # Test table information
            print("\n5. Testing table information...")
            try:
                # Try to get table info
                table_info = manager.client.table('user_topic_progress').select('*').limit(1).execute()
                print(f"   ✅ Table 'user_topic_progress' is accessible")
                print(f"   📊 Sample row structure: {list(table_info.data[0].keys()) if table_info.data else 'No data'}")
            except Exception as table_error:
                print(f"   ❌ Table access error: {table_error}")
                
                # Try alternative table names
                print("   🔍 Trying alternative table names...")
                alternative_tables = ['user_topic_progress', 'userTopicProgress', 'user_topic_progresses']
                for table_name in alternative_tables:
                    try:
                        test_query = manager.client.table(table_name).select('*').limit(1).execute()
                        print(f"      ✅ Table '{table_name}' exists and is accessible")
                        break
                    except:
                        print(f"      ❌ Table '{table_name}' not accessible")
            
        except Exception as debug_error:
            print(f"   ❌ Debug query failed: {debug_error}")
            import traceback
            traceback.print_exc()
        
        if progress_data:
            print("\n3. Progress data details:")
            for i, entry in enumerate(progress_data, 1):
                print(f"\n      Entry {i}:")
                print(f"        Full object: {entry}")
                print(f"        Keys available: {list(entry.keys())}")
                
                # Print each field individually for better readability
                for key, value in entry.items():
                    print(f"        {key}: {value}")
            
            # Test topic-specific methods if we have data
            if progress_data:
                first_entry = progress_data[0]
                topic = first_entry.get('topic')
                difficulty = first_entry.get('difficulty')
                
                if topic and difficulty:
                    print(f"\n4. Testing topic-specific progress for {topic} - {difficulty}...")
                    specific_progress = get_user_topic_difficulty_progress(test_user_id, topic, difficulty)
                    if specific_progress:
                        print(f"   ✅ Found specific progress: {specific_progress}")
                    
                    print(f"\n5. Testing topic summary for {topic}...")
                    topic_summary = get_user_topic_summary(test_user_id, topic)
                    print(f"   ✅ Topic summary: {topic_summary}")
        else:
            print("   ℹ️  No progress data found for this user")
        
        print("\n🎉 User Topic Progress GET operation completed!")
        return True
        
    except Exception as e:
        print(f"❌ User Topic Progress test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Supabase User Topic Progress Tests...\n")
    
    # Test basic connection
    if test_supabase_connection():
        # Test user topic progress GET operation
        test_user_topic_progress()
    else:
        print("\n❌ Basic connection failed. Please fix connection issues first.")
    
    print("\n✨ Test completed!") 
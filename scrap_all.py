from scrap import get_movie_reviews, get_movie_id
from pandas import read_csv
import time

def scrap_all_movies():
    df = read_csv("imdb_movies-1.csv")
    failed_movies = []

    for index, row in df.iterrows():
        if index < 333:
            continue
            
        print(f"The {index} movie in db starts processing...")
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                success = get_movie_reviews(row["id"])
                if success:
                    break
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying movie {row['id']} (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(5)  # Wait 5 seconds before retrying
            except Exception as e:
                print(f"Error processing movie {row['id']}: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(5)
        
        if retry_count == max_retries:
            failed_movies.append((index, row["id"]))
            print(f"Failed to process movie {row['id']} after {max_retries} attempts")
        
        # Wait between movies to avoid overwhelming the server
        time.sleep(2)

    # Print summary of failed movies
    if failed_movies:
        print("\nFailed movies summary:")
        for index, movie_id in failed_movies:
            print(f"Index: {index}, Movie ID: {movie_id}")

if __name__ == "__main__":
    scrap_all_movies()
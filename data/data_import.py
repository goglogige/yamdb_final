import csv
import sqlite3

if __name__ == '__main__':
    upload_data = {
        # 'titles.csv': 'INSERT INTO api_title (id, name, year, category_id) VALUES (?,?,?,?)',
        # 'category.csv': 'INSERT INTO api_category (id, name, slug) VALUES (?,?,?)',
        # 'genre.csv': 'INSERT INTO api_genre (id, name, slug) VALUES (?,?,?)',
        # 'genre_title.csv': 'INSERT INTO api_title_genre (id, title_id, genre_id) VALUES (?,?,?)',
        # 'users.csv': 'INSERT INTO api_user ('
        #              'id, username, email, role, description, first_name, last_name'
        #              ') VALUES (?,?,?,?,?,?,?)',
        'genre.csv': 'INSERT INTO api_genre (id, name, slug) VALUES (?,?,?)',
        'category.csv': 'INSERT INTO api_category(id, name, slug) VALUES (?,?,?)',
        'titles.csv': 'INSERT INTO api_title (id, name, year, category_id) VALUES (?,?,?,?)',
        'review.csv': 'INSERT INTO api_review (id, title_id, text, author_id, score, pub_date) VALUES (?,?,?,?,?,?)',
        'comments.csv': 'INSERT INTO api_comment (id, review_id, text, author_id, pub_date) VALUES (?,?,?,?,?)',
        'genre_title.csv': 'INSERT INTO api_title_genre (id, title_id, genre_id) VALUES (?,?,?)',
    }

    try:
        sqliteConnection = sqlite3.connect('../db.sqlite3', isolation_level=None)
        cursor = sqliteConnection.cursor()
        print("Successfully Connected to db.sqlite3")
        for data_file, sql_script in upload_data.items():
            with open(data_file, mode='r', encoding='utf-8') as review_file:
        # for data_file, sql_script in upload_data.items():
        #     with open(data_file, mode='r') as review_file:
                csv_reader = csv.DictReader(review_file)
                for row in csv_reader:
                    print(row)
                    count = cursor.execute(sql_script, tuple(row.values()))
                    print("Record inserted successfully ", cursor.rowcount)
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")


import csv
import sys
from django.core.management.base import BaseCommand
from main.db import questions_col

csv.field_size_limit(sys.maxsize)
class Command(BaseCommand):
    help = 'Import questions from a CSV file'

    def handle(self, *args, **kwargs):
        with open('/Users/shauryajain/root_19/compelted.csv', 'r') as file:  # Replace with your CSV file path
            reader = csv.DictReader(file)
            for row in reader:
                questions_col.update_one(
                    {'question_id': row['QuestionID']},
                    {'$set': {
                        'session_code': row['SessionCode'],
                        'session': row['Session'],
                        'year': int(row['Year']),
                        'paper_code': row['PaperCode'],
                        'variant': row['Variant'],
                        'file_question': row['File_Question'],
                        'subtopic': row['Subtopic'],
                        'extracted_text': row['ExtractedText'],
                        'image_base64': row['ImageBase64'],
                        'answer': row['Answer'],
                    }},
                    upsert=True
                )        self.stdout.write(self.style.SUCCESS('Successfully imported data!'))
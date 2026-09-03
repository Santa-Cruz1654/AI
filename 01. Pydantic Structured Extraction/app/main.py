from app.extractor import ExtractionError, extract_person


def main():
    text = """
    John Smith is 28 years old and works at Google
    as a Software Engineer. He has 5 years of experience.
    """

    try:
        person = extract_person(text)
        print(person)

    except ExtractionError as e:
        print(f"Extraction failed: {e}")


if __name__ == "__main__":
    main()
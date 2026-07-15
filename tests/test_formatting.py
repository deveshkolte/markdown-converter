"""Unit tests for the markdown formatting/cleanup pipeline."""

from markdown_converter.formatting import clean_markdown


class TestBulletReplacement:
    def test_cid_bullet_replaced(self) -> None:
        result = clean_markdown("(cid:127) Led migration project")
        assert result.strip() == "- Led migration project"

    def test_cid_bullet_with_indent(self) -> None:
        result = clean_markdown("  (cid:127) Indented item")
        assert result.strip() == "- Indented item"

    def test_unicode_bullet_replaced(self) -> None:
        result = clean_markdown("\u2022 Bullet item")
        assert result.strip() == "- Bullet item"

    def test_multiple_bullets_all_replaced(self) -> None:
        text = "\u2022 First\n\u2022 Second\n\u2022 Third"
        expected = "- First\n- Second\n- Third"
        assert clean_markdown(text) == expected

    def test_middle_of_text_bullet_preserved(self) -> None:
        text = "Skill A  \u2022  Skill B  \u2022  Skill C"
        result = clean_markdown(text)
        assert "\u2022" in result

    def test_blank_lines_not_affected(self) -> None:
        result = clean_markdown("(cid:127) Item\n\n(cid:128) Another")
        assert result.count("\n\n") == 1

    def test_inline_cid_converted_to_bullet(self) -> None:
        result = clean_markdown("Python (cid:127) Go (cid:127) Docker")
        assert " • " in result
        assert "(cid:127)" not in result
        assert result == "Python • Go • Docker"

    def test_inline_cid_line_start_not_affected(self) -> None:
        result = clean_markdown("(cid:127) Line start item")
        assert result == "- Line start item"


class TestHeadingConversion:
    def test_education_heading(self) -> None:
        text = "Some text\n\nEducation\n\nMore text"
        result = clean_markdown(text)
        assert "## Education" in result

        lines = result.split("\n")
        edu_idx = next(i for i, l in enumerate(lines) if "## Education" in l)
        assert lines[edu_idx - 1].strip() == ""
        assert lines[edu_idx + 1].strip() == ""

    def test_experience_heading(self) -> None:
        result = clean_markdown("\n\nExperience\n\n")
        assert "## Experience" in result

    def test_skills_heading_case_insensitive(self) -> None:
        result = clean_markdown("\n\nTECHNICAL SKILLS\n\n")
        assert "## TECHNICAL SKILLS" in result

    def test_interests_heading(self) -> None:
        result = clean_markdown("\n\nInterests\n\n")
        assert "## Interests" in result

    def test_not_a_heading_if_not_surrounded_by_blanks(self) -> None:
        text = "This Education is not a heading"
        result = clean_markdown(text)
        assert "## Education" not in result

    def test_all_caps_name_not_converted(self) -> None:
        text = "JOHN DOE\n\nSome text"
        result = clean_markdown(text)
        assert "## JOHN DOE" not in result

    def test_long_line_not_converted(self) -> None:
        text = "\n\n" + "X" * 90 + "\n\n"
        result = clean_markdown(text)
        assert "## " not in result

    def test_multiple_headings(self) -> None:
        text = "\n\nEducation\n\nSome content\n\nSkills\n\nMore\n\nProjects"
        result = clean_markdown(text)
        assert "## Education" in result
        assert "## Skills" in result
        assert "## Projects" in result


class TestSpacingPreservation:
    def test_no_duplicate_blank_lines(self) -> None:
        text = "A\n\n\n\nB"
        result = clean_markdown(text)
        assert result == "A\n\nB"

    def test_many_blank_lines_collapsed(self) -> None:
        text = "A\n\n\n\n\n\nB"
        result = clean_markdown(text)
        assert result == "A\n\nB"

    def text_leading_trailing_blanks_preserved(self) -> None:
        text = "\n\nA\n\n"
        result = clean_markdown(text)
        assert result == "\n\nA\n\n"


class TestFormFeedRemoval:
    def test_form_feed_removed(self) -> None:
        text = "Some text\x0cMore text"
        result = clean_markdown(text)
        assert "\x0c" not in result

    def test_bullet_with_form_feed(self) -> None:
        text = "\x0c\u2022 Item after form feed"
        result = clean_markdown(text)
        assert "Item after form feed" in result
        assert "\x0c" not in result


class TestContentPreservation:
    def test_text_not_altered(self) -> None:
        text = "Hello World\nThis is a test."
        result = clean_markdown(text)
        assert result == text

    def test_section_content_preserved(self) -> None:
        text = "Education\n\nBachelor of Science in Computer Science"
        result = clean_markdown(text)
        assert "Bachelor of Science in Computer Science" in result

    def test_inline_bold_preserved(self) -> None:
        text = "This is **bold** and *italic* text"
        result = clean_markdown(text)
        assert "**bold**" in result
        assert "*italic*" in result

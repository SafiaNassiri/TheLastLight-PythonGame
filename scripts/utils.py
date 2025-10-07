def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines, current_line = [], ''
    for word in words:
        test = current_line + (' ' if current_line else '') + word
        if font.size(test)[0] <= max_width:
            current_line = test
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

import time

def event_card_HTML(event_json):
    """Returns the HTML for an event card"""

    # Limits str to n chars and adds ' ...' if it's longer
    capped_str = lambda s, n: s[:n] + ' ...' if len(s) > n else s

    # Returns v if k is not in d or if d[k] is empty
    v_empy_get = lambda d, k, v: d[k] if k in d and d[k].strip() else v
    
    _, month, day = event_json['date_start'].split('-')
    month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][int(month)-1]

    time_start_hr, time_start_min = v_empy_get(event_json, 'time_start',' ? : ? ').split(':')[:2]
    time_end_hr, time_end_min = v_empy_get(event_json, 'time_end',' ? : ? ').split(':')[:2]

    datetime = f'{month} {day} {time_start_hr}:{time_start_min} - {time_end_hr}:{time_end_min}'

    subtitle = '. '.join([datetime, event_json['event_type'], event_json['building_name']])
    
    html = f"""
    <div class="card" style="margin-bottom:8px;">
        <div class="card-body">
            <h5 class="card-title">{event_json['combined_title']}</h5>
            <h6 class="card-subtitle mb-2 text-muted">{subtitle}</h6>
            <p class="card-text">{capped_str(event_json['description'], 500)}</p>
            <a href="{event_json['permalink']}" class="card-link" target="_blank">Event Link</a>
        </div>
    </div>
    """
    
    return html

def highlight_keywords(event_json, keyword):
    """Bolds keywords in the event description"""

    for field in ['combined_title', 'description']:
        for kw in [keyword, keyword.title()]:
            event_json[field] = event_json[field].replace(kw, f'<b>{kw}</b>')
    return event_json

def update_page(gpt_events_json, keyword_events, template_file='template.html', output_file='index.html'):
    """Updates the page with the week's events"""
    
    with open(template_file, 'r') as f: template = f.read()

    with open(output_file, 'w') as f:

        # Events recommended by GPT
        template = template.replace('{{gpt-events}}', '\n'.join([event_card_HTML(event_json) for event_json in gpt_events_json]))

        # Stats
        template = template.replace('{{updated}}', str(time.time()*1000))

        # Events with keywords
        if keyword_events:
            kw_txt = "<h1 style='text-align:center;'>Events with keywords</h1>"
            for keyword, events in keyword_events.items():
                if events: kw_txt += f"<br><h2 style='text-align:center;'>\"{keyword}\"</h2>"
                for event_json in events:
                    kw_txt += event_card_HTML(highlight_keywords(event_json, keyword))
            template = template.replace('{{keyword-events}}', kw_txt)
        
        else:
            template = template.replace('{{keyword-events}}', '')

        f.write(template)

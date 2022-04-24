from flask import Flask
from flask import url_for, render_template, request, redirect
import psycopg2

app = Flask(__name__)

def connect_to_database():
    conn = psycopg2.connect(dbname="dwvsxvkk",
                            user="dwvsxvkk",
                            password="8EorB3Yja9hb-LBNQcppetviJSdnsKj6",
                            host="isilo.db.elephantsql.com")

    c = conn.cursor()
    return c, conn


def check_empty(arg_list):
    if arg_list == [""]:
        return list()
    else:
        return arg_list

@app.route('/')
def index():
    c, conn = connect_to_database()
    c.execute(f"""SELECT * FROM frames""")
    frames = [key[1] for key in c.fetchall()]
    c.execute(f"""SELECT * FROM verbs""")
    verbs = [key[1] for key in c.fetchall()]
    c.execute(f"""SELECT * FROM metaphors""")
    metaphors = [key[1] for key in c.fetchall()]
    c.execute(f"""SELECT * FROM stems""")
    stems = [key[1] for key in c.fetchall()]
    c.execute(f"""SELECT * FROM fields""")
    fields = [key[1] for key in c.fetchall()]
    c.execute(f"""SELECT * FROM glosses""")
    glosses = [key[1] for key in c.fetchall()]
    #conn.close()
    return render_template('index.html', fields=fields,
                           frames=frames, glosses=glosses,
                           metaphors=metaphors, stems=stems,
                           verbs=verbs)


@app.route('/team')
def team():
    return render_template('team.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/process_data', methods=['get'])
def process_data():
    c, conn = connect_to_database()
    if not request.args:
        return redirect(url_for('index'))
    field = check_empty(request.args.getlist('field'))
    frame = check_empty(request.args.getlist('frame'))
    metaphor = check_empty(request.args.getlist('metaphor'))
    verb = check_empty(request.args.getlist('verb'))
    stem = check_empty(request.args.getlist('stem'))
    glosses = check_empty(request.args.getlist('glosses'))
    c.execute("""WITH glosses
                            AS(
                                SELECT example_id, gloss
                            FROM example2gloss
                            LEFT JOIN glosses using(gloss_id)),
                            frames AS(
                                SELECT frame_id, frame, field
                                FROM frames
                                LEFT JOIN fields using(field_id))
                            SELECT example, translation, source, frame, field, verb, 
                            metaphor, gloss_row, stem                        
                            FROM examples
                            LEFT JOIN glosses using(example_id)
                            LEFT JOIN frames using(frame_id)
                            LEFT JOIN verbs using(verb_id)
                            LEFT JOIN stems using(stem_id)
                            LEFT JOIN metaphors using(metaphor_id)
                            WHERE (%(gloss)s='{}' OR gloss=ANY(%(gloss)s))
                            AND (%(frame)s='{}' OR frame=ANY(%(frame)s))
                            AND (%(field)s='{}' OR field=ANY(%(field)s))
                            AND (%(verb)s='{}' OR verb=ANY(%(verb)s))
                            AND (%(stem)s='{}' OR stem=ANY(%(stem)s))
                            AND (%(metaphor)s='{}' OR metaphor=ANY(%(metaphor)s))
                            GROUP BY example, translation, source, frame, field, verb, 
                            metaphor, gloss_row, stem
                            ORDER BY COUNT(example) DESC""", {"gloss": glosses, "field": field,
                                                              "frame": frame, "verb": verb,
                                                              "stem": stem, "metaphor": metaphor, })
    results = c.fetchall()
    conn.close()
    if results:
        return render_template('results.html', results=results, num_examples=len(results))
    else:
        return render_template('no_results.html')


if __name__ == '__main__':
    app.run()

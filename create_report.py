from collections import defaultdict
import argparse
from pathlib import Path
import jinja2
from jinja2 import Template
import shutil


def parse_dir(dir, cols=None, whitelist=None, sort_by_whitelist=True, ext=".wav"):
    files = [f for f in dir.glob(f"**/*{ext}")]
    print(cols)

    out = defaultdict(dict)
    for i, f in enumerate(files):
        col, desc = f.parent.stem, f.stem
        id = desc
        if cols is not None and col not in cols:
            continue
        if whitelist is not None and desc not in whitelist:
            continue
        trg_dir = Path(str(f.parent).replace("/samples/", "/samples_final/"))
        trg_dir.mkdir(parents=True, exist_ok=True)
        trg_path = trg_dir / f.name
        shutil.copy(f, trg_path)
        col = cols[col]
        out[id][col] = f.parent.name + "/" + f.name
        out[id]["desc"] = " ".join(desc.split("_"))

    if sort_by_whitelist:
        # sort dict according to the whitelist (lets you control the order of samples)
        out = dict(sorted(out.items(), key=lambda pair: whitelist.index(pair[0])))

    return out


def get_cols(parsed_dir):
    cols = []
    for k, v in parsed_dir.items():
        cols += v.keys()
    return list(sorted(set(cols)))


def create_table(parsed_dir, cols=None, title=""):
    template = Template("""
    <center>
    <h1>{{ title }}</h1>
    <table class="pure-table">
        <thead>
        <tr>
            {% for col in cols %}
            <td>{{ col }}</td>
            {% endfor %}
        </tr>
        </thead>

        <tbody>
        {% for id in parsed_dir %}
        {% if loop.index % 2 != 0 %}
        <tr class="pure-table-odd">
        {% else %}
        <tr>
        {% endif %}

            {% for col in cols %}
            {% if parsed_dir[id][col].endswith(".wav") %}
            <td><audio controls style="width: 250px;"><source src="{{ parsed_dir[id][col] }}" type="audio/wav"></audio></td>
            {% else %}
            <td>{{ parsed_dir[id][col] }}</td>
            {% endif %}
            {% endfor %}
        </tr>
        {% endfor %}
        </tbody>
    </table>
    </center>
    """)

    cols = get_cols(parsed_dir) if cols is None else cols.values()
    return template.render(cols=cols, parsed_dir=parsed_dir, title=title)


def create_html(content):
    template = Template("""
    <html>
    <head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/purecss@2.1.0/build/pure-min.css" integrity="sha384-yHIFVG6ClnONEA5yB5DJXfW2/KC173DIQrYoZMEtBvGzmf0PKiGyNEqe9N6BNDBH" crossorigin="anonymous">
    </head>
    <title>Samples</title>
    <body>
    {{ content }}
    </body>
    </html>
    """)
    return template.render(content=content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", type=Path)
    args = parser.parse_args()

    tables = []

    title = "AudioGen vs. baselines"
    algos = {
        "desc": "desc",
        "32factor_1streams_2048codesPerBook_noMixing": "AudioGen-base no mixing",
        "32factor_1streams_2048codesPerBook": "AudioGen-base with mixing",
        "large_32factor_1streams_2048codesPerBook": "AudioGen-large with mixing",
        "diffsound_trim": "DiffSound",
        "gt_trim": "Ground Truth",
    }
    files = [
        "a_man_speaks_as_birds_chirp_and_dogs_bark",
        "whistling_with_wind_blowing",
        "male_speaking_with_many_people_cheering_in_background",
        "a_man_is_speaking_while_typing_on_a_keyboard",
        "a_cat_meowing_and_young_female_speaking",
        "a_duck_quacking_as_birds_chirp_and_a_pigeon_cooing",
        "a_blaring_siren_from_a_vehicle_passes_by_then_echoes_and_fades_into_the_distance",
        "a_baby_continuously_crying",
        "continuous_laughter_and_chuckling",
        "railroad_crossing_signal_followed_by_a_train_passing_and_blowing_horn",
    ]
    tables += [create_table(parse_dir(args.dir, cols=algos, whitelist=files), cols=algos, title=title)]

    title = "Classifier-free guidance"
    algos = {
        "desc": "desc",
        "large_32factor_1streams_2048codesPerBook_cfg1": "gamma=1",
        "large_32factor_1streams_2048codesPerBook_cfg2": "gamma=2",
        "large_32factor_1streams_2048codesPerBook_cfg3": "gamma=3",
        "large_32factor_1streams_2048codesPerBook_cfg4": "gamma=4",
        "large_32factor_1streams_2048codesPerBook_cfg5": "gamma=5",
    }
    # files = ["a_cat_meowing_twice", "a_baby_continuously_crying"]
    tables += [create_table(parse_dir(args.dir, cols=algos, whitelist=files), cols=algos, title=title)]

    "* Under the 'Random audio prompt' column we feed the model with random audio as prompt, and the text condition from the 'desc' column"
    title = "Audio continuation from 1s"
    algos = {
        "desc": "desc",
        "len4_audioCont_audioPrefix1_noText": "No text",
        "len4_audioCont_audioPrefix1": "Original text",
        "len4_audioCont_audioPrefix1_randomText": "Random audio prompt",
    }
    files_audio_cont = [
        "a_man_speaks_as_birds_chirp_and_dogs_bark",
        "a_baby_continuously_crying",
        "a_man_is_speaking_while_typing_on_a_keyboard",
        "a_cat_meowing_and_young_female_speaking",
        "continuous_laughter_and_chuckling",
        "railroad_crossing_signal_followed_by_a_train_passing_and_blowing_horn",
        "male_speaking_with_many_people_cheering_in_background",
        "a_blaring_siren_from_a_vehicle_passes_by_then_echoes_and_fades_into_the_distance",
        "a_duck_quacking_as_birds_chirp_and_a_pigeon_cooing",
        "whistling_with_wind_blowing",
    ]
    tables += [create_table(parse_dir(args.dir, cols=algos, whitelist=files_audio_cont), cols=algos, title=title)]

    title = "Multi-stream (large)"
    algos = {
        "desc": "desc",
        "large_32factor_1streams_2048codesPerBook": "1 stream",
        "large_64factor_2streams_1024codesPerBook": "2 streams",
        "large_128factor_4streams_512codesPerBook": "4 streams"
    }
    # files = ["a_cat_meowing_twice", "a_baby_continuously_crying"]
    tables += [create_table(parse_dir(args.dir, cols=algos, whitelist=files), cols=algos, title=title)]

    html = create_html("".join(tables))
    open(args.dir / "report.html", "w").write(html)


if __name__ == "__main__":
    main()

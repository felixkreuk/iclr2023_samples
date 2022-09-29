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
    </br>
    """)

    cols = get_cols(parsed_dir) if cols is None else cols.values()
    return template.render(cols=cols, parsed_dir=parsed_dir, title=title)


def create_html(content, title=""):
    template = Template("""
    <html>
    <head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/purecss@2.1.0/build/pure-min.css" integrity="sha384-yHIFVG6ClnONEA5yB5DJXfW2/KC173DIQrYoZMEtBvGzmf0PKiGyNEqe9N6BNDBH" crossorigin="anonymous">
    <style>
        .container{
            position: relative;
            background:  rgb(22, 38, 67); /* For browsers that do not support gradients */
            /* background: -webkit-linear-gradient(color1, color2); /* For Safari 5.1 to 6.0 */
            /* background: -o-linear-gradient(color1, color2); /* For Opera 11.1 to 12.0 */
            /* background: -moz-linear-gradient(color1, color2); /* For Firefox 3.6 to 15 */
            /* background: linear-gradient(color1, color2);  /* Standard syntax */
            background-size: cover;
            height: auto;
            padding: 2%;
        }
    </style>
    </head>
    <title>Samples</title>
    <div class="container" align="center" style="color:white;">
        <h1>AudioGen: Textually Guided Audio Generation</h1>
        <h3><a href="https://felixkreuk.github.io" style="color:white;">Felix Kreuk</a>, Gabriel Synnaeve, Adam Polyak, Uriel Singer, Alexandre Défossez, Jade Copet, Devi Parikh, Yaniv Taigman, Yossi Adi</h3>
        <p style="text-align: justify; width: 50%">
        We tackle the problem of generating audio samples conditioned on descriptive text captions. In this work, we propose AudioGen, an auto-regressive generative model that generates audio samples conditioned on text inputs. AudioGen operates on a learnt discrete audio representation. The task of text-to-audio generation poses multiple challenges. Due to the way audio travels through a medium, differentiating ``objects'' can be a difficult task (e.g., separating multiple people simultaneously speaking). This is further complicated by real-world recording conditions (e.g., background noise, reverberation, etc.). Scarce text annotations impose another constraint, limiting the ability to scale models. Finally, modeling high-fidelity audio requires encoding audio at high sampling rate, leading to extremely long sequences. To alleviate the aforementioned challenges we propose an augmentation technique that mixes different audio samples, driving the model to internally learn to separate multiple sources. We curated 10 datasets containing different types of audio and text annotations to handle the scarcity of text-audio data points. For faster inference, we explore the use of multi-stream modeling, allowing the use of shorter sequences while maintaining a similar bitrate and perceptual quality. We apply classifier-free guidance to improve adherence to text. Comparing to the evaluated baselines, AudioGen outperforms over both objective and subjective metrics. Finally, we explore the ability of the proposed method to generate audio continuation conditionally and unconditionally.
        </p>
    </div>
    <body>
    {{ content }}
    </body>
    </html>
    """)
    return template.render(content=content, title=title)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", type=Path)
    args = parser.parse_args()

    tables = []

    title = "AudioGen samples"
    algos = {
        "desc": "desc",
        "32factor_1streams_2048codesPerBook_noMixing": "AudioGen-base no mixing",
        "32factor_1streams_2048codesPerBook": "AudioGen-base with mixing",
        "large_32factor_1streams_2048codesPerBook": "<b>AudioGen-large with mixing</b>",
        "diffsound_trim": "DiffSound",
        "gt_trim": "Ground Truth",
    }
    files = [
        "a_man_speaks_as_birds_chirp_and_dogs_bark",
        "whistling_with_wind_blowing",
        "male_speaking_with_many_people_cheering_in_background",
        "a_man_is_speaking_while_typing_on_a_keyboard",
        "sirens_and_a_humming_engine_approach_and_pass",
        "male_speech_with_horns_honking_in_the_background",
        "drums_and_music_playing_with_a_man_speaking",
        "beep_then_male_speaking_multiple_times",
        "a_cat_meowing_and_young_female_speaking",
        "a_man_speaking_followed_by_another_man_speaking_in_the_background_as_a_motorcycle_engine_runs_idle",
        "a_duck_quacking_as_birds_chirp_and_a_pigeon_cooing",
        "a_baby_continuously_crying",
        "continuous_laughter_and_chuckling",
    ]
    tables += [create_table(parse_dir(args.dir, cols=algos, whitelist=files), cols=algos, title=title)]

    html = create_html("".join(tables), title="AudioGen: Textually Guided Audio Generation")
    open(args.dir / "report.html", "w").write(html)


if __name__ == "__main__":
    main()

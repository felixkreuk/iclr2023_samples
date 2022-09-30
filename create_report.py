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


def create_table(parsed_dir, cols=None, title="", text=""):
    template = Template("""
    <div class="container" id="abstractdiv">
        <h2>{{ title }}</h2>
        {{ text }}
        <table class="table table-responsive">
            <thead>
            <tr class="text-center">
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
                <td class="text-center"><audio controls style="width: 150px;"><source src="{{ parsed_dir[id][col] }}" type="audio/wav"></audio></td>
                {% else %}
                <td>{{ parsed_dir[id][col] }}</td>
                {% endif %}
                {% endfor %}
            </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
    """)

    cols = get_cols(parsed_dir) if cols is None else cols.values()
    return template.render(cols=cols, parsed_dir=parsed_dir, title=title, text=text)


def create_html(content, title=""):
    template = Template("""
    <html>
    <head>
    
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
          integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <link href='http://fonts.googleapis.com/css?family=Lato:300,400,900' rel='stylesheet' type='text/css'>
    <link href="style.css" rel="stylesheet">
    <title>AudioGen: Textually Guided Audio Generation</title>
    </head>
    <body>

    <div id="header" class="container-fluid">
    <div class="row" style="text-align: center;"/>
    <!--<div class="logoimg">
        <img src="meta_logo.png" height="95">
        <img src="huji_logo.png" height="95">
    </div>-->
	<div class="row">
        <h1>AudioGen: Textually Guided Audio Generation</h1>
        <div class="authors">
            <a href="https://felixkreuk.github.io">Felix Kreuk</a><sup>1</sup>, 
            Gabriel Synnaeve<sup>1</sup>, 
            Adam Polyak<sup>1</sup>, 
            Uriel Singer<sup>1</sup>, 
            Alexandre Défossez<sup>1</sup></br> 
            Jade Copet<sup>1</sup>, 
            Devi Parikh<sup>1</sup>, 
            Yaniv Taigman<sup>1</sup>, 
            Yossi Adi<sup>1,2</sup></h3>
        </div>

        <br>
        <p><sup>1</sup>FAIR Team, Meta AI</p>
        <p><sup>2</sup>The Hebrew University of Jerusalem</p>

		<div class="assets">
			<a href="" target="_blank">[paper]</a>
			<a href="" target="_blank">[code]</a>
		</div>
    </div>
    </div>

    <div class="container">
        <h2>Abstract</h2>
        <span>
            We tackle the problem of generating audio samples conditioned on descriptive text captions. In this work, we propose AudioGen, an auto-regressive generative model that generates audio samples conditioned on text inputs. AudioGen operates on a learnt discrete audio representation. The task of text-to-audio generation poses multiple challenges. Due to the way audio travels through a medium, differentiating ``objects'' can be a difficult task (e.g., separating multiple people simultaneously speaking). This is further complicated by real-world recording conditions (e.g., background noise, reverberation, etc.). Scarce text annotations impose another constraint, limiting the ability to scale models. Finally, modeling high-fidelity audio requires encoding audio at high sampling rate, leading to extremely long sequences. To alleviate the aforementioned challenges we propose an augmentation technique that mixes different audio samples, driving the model to internally learn to separate multiple sources. We curated 10 datasets containing different types of audio and text annotations to handle the scarcity of text-audio data points. For faster inference, we explore the use of multi-stream modeling, allowing the use of shorter sequences while maintaining a similar bitrate and perceptual quality. We apply classifier-free guidance to improve adherence to text. Comparing to the evaluated baselines, AudioGen outperforms over both objective and subjective metrics. Finally, we explore the ability of the proposed method to generate audio continuation conditionally and unconditionally.
        </span>
    </div>

    <div class="container">
        <h2>Samples</h2>
        <div class="text-center">
            <video width="80%" controls>
                <source src="audiogen_teaser.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
    </div>

    <div class="container" id="abstractdiv">
        <h2>Architecture</h2>
        <img src="audiogen_arch.png" width="100%">
    </div>
    
    {{ content }}

    <div class="container">
        <h2>BibTeX</h2>
        <pre class="citation">
            @inproceedings{,
            author    = {},
            title     = {},
            booktitle = {},
            year      = {}
            }
        </pre>
    </div>

    </body>
    </html>
    """)
    return template.render(content=content, title=title)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", type=Path)
    args = parser.parse_args()

    tables = []

    title = "Samples: comparison to prior work"
    algos = {
        "desc": "desc",
        "large_32factor_1streams_2048codesPerBook": "<b>AudioGen-large with mixing</b>",
        "32factor_1streams_2048codesPerBook": "AudioGen-base with mixing",
        "32factor_1streams_2048codesPerBook_noMixing": "AudioGen-base no mixing",
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

    title = "Classifier-free guidance"
    text = "An ablation study on the affect of the guidance scale parameter."
    algos = {
        "desc": "desc",
        "large_32factor_1streams_2048codesPerBook_cfg1": "gamma=1",
        "large_32factor_1streams_2048codesPerBook_cfg2": "gamma=2",
        "large_32factor_1streams_2048codesPerBook_cfg3": "gamma=3",
        "large_32factor_1streams_2048codesPerBook_cfg4": "gamma=4",
        "large_32factor_1streams_2048codesPerBook_cfg5": "gamma=5",
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
    tables += [create_table(parse_dir(args.dir, cols=algos, whitelist=files), cols=algos, title=title, text=text)]

    title = "Audio continuation: 1 second audio prompt + text/no-text"
    text = "Examples of audio continuation given 1 second audio prompts and various text conditioning settings. Under the 'random audio prompt + text condition' column we use condition the model on a random audio prompt together with the text condition under the 'desc' column."
    algos = {
        "desc": "desc",
        "len4_audioCont_audioPrefix1_noText": "no text",
        "len4_audioCont_audioPrefix1": "text condition",
        "len4_audioCont_audioPrefix1_randomText": "random audio prompt + text condition",
    }
    files = [
        "thundering_sounds_while_rain_pours",
        "a_man_is_speaking_while_typing_on_a_keyboard", # resample no text
        "speech_and_a_goat_bleating",
        "subway_train_blowing_its_horn.",
        "a_baby_continuously_crying", # resample no text
        "a_bird_cawing_followed_by_an_infant_crying",
        "a_crowd_applauds_followed_by_a_woman_and_a_man_speaking",
        # "a_dog_barks_quickly",
        "a_faint_siren_followed_by_a_man_speaking_and_wooing",
    ]
    tables += [create_table(parse_dir(args.dir, cols=algos, whitelist=files), cols=algos, title=title, text=text)]

    title = "Multi-stream modeling"
    text = ""
    algos = {
        "desc": "desc",
        "large_32factor_1streams_2048codesPerBook": "1 stream",
        "large_64factor_2streams_1024codesPerBook": "2 streams",
        "large_128factor_4streams_512codesPerBook": "4 streams",
    }
    files = [
        "typing_on_a_typewriter", 
        "the_siren_of_an_emergency_vehicle_sounds", 
        "the_rhythmic_and_repeated_ticktock_of_a_clock", 
        "several_gunshots_firing_followed_by_two_men_talking_then_music_playing", 
        "railroad_crossing_signal_followed_by_a_train_passing_and_blowing_horn", 
        "pigeons_coo_with_some_rustling", 
    ]
    tables += [create_table(parse_dir(args.dir, cols=algos, whitelist=files), cols=algos, title=title, text=text)]

    html = create_html("".join(tables), title="AudioGen: Textually Guided Audio Generation")
    open(args.dir / "report.html", "w").write(html)


if __name__ == "__main__":
    main()

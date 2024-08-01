import streamlit as st
import openai
import pysrt
import tempfile
import os
import bisect

# Streamlit app
st.title("Subtitle Enhancer")

# Input for OpenAI API Key
api_key = st.text_input("Enter your OpenAI API key", type="password")

# Set up OpenAI client
if api_key:
    openai.api_key = api_key

# File uploaders for the MP3 and SRT files
uploaded_mp3 = st.file_uploader("Upload MP3 file", type="mp3")
uploaded_srt = st.file_uploader("Upload SRT file", type="srt")


def enhance_subtitles(subtitles, transcribed_words):
    # Prepare subtitle timing and text storage
    subtitle_times = [(sub.start.ordinal, sub.end.ordinal) for sub in subtitles]
    subtitle_texts = [[] for _ in subtitles]

    # Process each word in the transcribed words
    for word in transcribed_words:
        word_time = word['start'] * 1000
        # Find the appropriate subtitle index using binary search for efficiency
        pos = bisect.bisect_right(subtitle_times, (word_time,))

        # If the word time is after the last subtitle, adjust pos to the last subtitle
        if pos == len(subtitles):
            pos -= 1
        elif pos < len(subtitles) and word_time > subtitle_times[pos - 1][1]:
            # No need to adjust pos, word goes to the next block if it's out of current range
            pass
        else:
            # If word falls before the beginning of any subtitles and not between, adjust pos
            pos -= 1

        # Append the word to the appropriate subtitle text list
        subtitle_texts[pos].append(word['word'])

    # Update subtitles with collected texts
    enhanced_subs = pysrt.SubRipFile()
    for idx, sub in enumerate(subtitles):
        sub.text = ' '.join(subtitle_texts[idx])
        enhanced_subs.append(sub)

    return enhanced_subs



def send_to_gpt4_for_improvement(subtitles):
    srt_text = '\n'.join([str(sub) for sub in subtitles])
    st.text_area("Subtitle analysis successful! (Step 2/3)", srt_text, height=300)
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Improve the grammatical quality of these srt subtitles without changing any of the timings and answer in the language of the original subtitles:"},
            {"role": "user", "content": srt_text}
        ]
    )
    return response.choices[0].message['content']


if st.button("Enhance Subtitles"):
    if uploaded_mp3 is not None and uploaded_srt is not None and api_key:
        # Handle the MP3 file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_mp3:
            tmp_mp3.write(uploaded_mp3.getvalue())
            tmp_mp3.flush()  # Ensure all data is written to the file
            transcription = openai.Audio.transcribe(
                model="whisper-1",
                file=open(tmp_mp3.name, "rb"),
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )
            transcription_data = transcription.words
            st.text_area("Audio analysis successful! (Step 1/3)", transcription.words, height=300)

        # Handle the SRT file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".srt", mode='wb') as tmp_srt:
            tmp_srt.write(uploaded_srt.getvalue())
            tmp_srt.flush()  # Ensure all data is written to the file
            subs = pysrt.open(tmp_srt.name, encoding='utf-8')

        # Extract the base name of the uploaded SRT file without the extension
        srt_base_name = os.path.splitext(uploaded_srt.name)[0]

        # Enhance subtitles using the provided function
        enhanced_subtitles = enhance_subtitles(subs, transcription_data)
        st.write("Subtitle analysis successful! 2/3")

        # Send the improved subtitles to GPT-4 for grammatical improvement
        if enhanced_subtitles:
            grammatically_improved_subtitles = send_to_gpt4_for_improvement(enhanced_subtitles)
            st.text_area("Grammatically Improved Subtitles", grammatically_improved_subtitles, height=300)

            # Save the grammatically improved subtitles to a temporary file and provide download
            with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as temp_file:
                temp_file.write(grammatically_improved_subtitles.encode('utf-8'))
                temp_file.flush()
                temp_file.close()  # Ensure the file is properly closed
                with open(temp_file.name, 'rb') as file_to_download:
                    enhanced_file_name = f"{srt_base_name}_enhanced.srt"
                    st.download_button(label="Download Grammatically Enhanced SRT",
                                       data=file_to_download.read(),
                                       file_name=enhanced_file_name,
                                       mime="text/plain")
        else:
            st.write("No subtitles were enhanced.")
    elif not api_key:
        st.error("Please enter your OpenAI API key.")

st.markdown("---")
st.write("")

st.header("How to use")
st.write(
    "Enhancing subtitles has never been easier, especially for Swiss German subtitles! The Subtitle Enhancer was created to handle the complexities of Swiss German, a task where most editing software falls short. However, it works seamlessly with all languages supported by GPT-4o and Whisper. Just follow these simple steps to get started and make your videos more accessible and professional."
)
st.write("""
Before you start, please complete the following prerequisites:

1. **Create an OpenAI Account and Generate an API Key:**
   - Make sure you have an OpenAI account and generate an API key. For guidance, refer to this [article](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key).
   - Add only a small amount of funds to your OpenAI account, as this app is experimental and lacks security measures.
   - Please be advised that the creator acts in good faith; however, the creator disclaims any liability for the theft or misuse of the API key by others. By using this tool, you agree not to hold the creator liable for any claims, damages, or other liabilities. This tool is provided under the MIT License, which states:
        - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
   - You can view the source code by clicking on the GitHub icon in the menu.

2. **Export Video or Speaker Track as MP3:**
   - Export your video or its speaker track as an MP3 file.

3. **Auto-Create Subtitles:**
   - Use a software like Premiere Pro to auto-generate and export srt subtitles.
   - Adjust the timings to your liking before using this tool for the best results.

Steps to use the app:

1. **Enter Your OpenAI API Key:**
   - Input your OpenAI API key in the provided text box.

2. **Upload Files:**
   - Upload the MP3 file of your audio.
   - Upload the corresponding SRT file for the subtitles.

3. **Enhance Subtitles:**
   - Click on the "Enhance Subtitles" button.
   - The app will analyze and synchronize the subtitles with the audio.

4. **Grammatical Improvement:**
   - The synchronized subtitles are then sent to GPT-4o for grammatical enhancement.

5. **Download the Enhanced Subtitles:**
   - Once the process is complete, download the grammatically improved SRT file.

6. **Import into Editing Software:**
   - Import the enhanced SRT file back into your editing software and finish your project.
""")

# Custom CSS
st.markdown(
    """
    <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');

            .appview-container {
                animation: fadeInSlideUp 1s ease-in-out forwards;
            }

            h1 {
                font-family: "DM Serif Display", serif;
                color: #000;
                font-weight: 500;
                font-size: calc(1.475rem + 1.85vw);
                margin-top: 30px;
                margin-bottom: 20px;
            }

            h2{
                font-family: "DM Serif Display", serif;
                color: #000;
                font-weight: 500;
            }
            
            a {
                color: rgb(255, 185, 80)!important;
            }

            @media (min-width: 1320px) {
                h1 {
                    font-size: 3rem;
                }
            }

            p {
                font-family: "Inter", sans-serif;
            }

            header{
            background: transparent!important;
            pointer-events: none; /* Allow clicks to pass through */
            }

            header * {
            pointer-events: initial;
            }

            #navbar {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                padding-top: 0rem;
                background:white;
                z-index: 100;
            }

            #logocontainer {
                max-width: 1320px;
                margin: auto;
                padding: 8px 20px 8px 20px;
            }

            #logo {
                box-shadow: none !important;
                height: 55px;
                z-index: 1000000000;
                margin-top: .40625rem;
                margin-bottom: .40625rem;
            }

            .element-container div div:has(> img) {
                width: 100%;
                display: flex;
            }

            .element-container div div img {
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5);
                margin: auto;
            }

            @keyframes fadeInSlideUp {
                0% {
                    opacity: 0;
                }
                100% {
                    opacity: 1;
            }
    </style>
    <div id="navbar">
        <div id="logocontainer">
            <a href="https://xn--gbs-qla.com/" target="_blank">
                <img src="https://xn--gbs-qla.com/assets/images/logo/logo-dark.svg" class="logo" id="logo">
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True
)

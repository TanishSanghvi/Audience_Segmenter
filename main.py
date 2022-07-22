
from flask import Flask, request, render_template,redirect,url_for,session, Response
from authentication import YoutubeAuthentication
from comments import YoutubeComments
from user_playlists import Playlists
from __tags_process__ import Tags
from _clustering_ import Clusters
import pandas as pd
import time
import os
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import webbrowser
from threading import Timer

app = Flask(__name__)

youtube=''

def open_browser():
      webbrowser.open_new('http://localhost:8080/')

@app.route("/", methods =["GET", "POST"])
def connect():
    msg = None
    if request.method == "POST":
       global youtube
       developer_key = request.form.get("developer_key")

       youtube_auth = YoutubeAuthentication(developer_key=developer_key)
       try:

            youtube = youtube_auth.connect_google_api()

            #session['y'] = youtube
            return redirect(url_for('run_hack'))
       except:
           msg = 'Incorrect Developer key' #add pop up
           return redirect(url_for('connect',msg = msg))

    return render_template("form.html")

final_df = pd.DataFrame()

@app.route("/video", methods =["GET", "POST"])
def run_hack():
    global final_df
    if request.method == "POST":
        video_id = request.form.get("videoids")
        videos_list = list(video_id.split())
        comments = YoutubeComments(youtube=youtube, videos_list=videos_list)
        comments_df = comments.get_comments()
        playlist = Playlists(youtube=youtube)
        playlist_df = playlist.pull_playlists(comments_df)
        videos_df = playlist.get_videos(playlist_df)
        tags = Tags(youtube=youtube)
        tags_df = tags.pull_tags(videos_df)
        final_df = tags.process(videos_df, playlist_df, tags_df)
        
        return redirect(url_for('mpl'))
    
    return render_template("video.html")


@app.route('/matplot', methods=("POST", "GET"))
def mpl():
    return render_template('matplot.html',
                           PageTitle = "Matplotlib")

@app.route('/plot')
def plot_png():
    clust = Clusters(final_df) 
    labels, Nc, score, pca_d, = clust.segmentation()
    
    fig = create_figure(labels, Nc, score, pca_d)
    output = io.BytesIO()

    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure(labels, Nc, score, pca_d):
    fig, ax = plt.subplots(2)
    
    ax[0].plot(Nc, score)
    ax[0].set_xlabel('Number of Clusters')
    ax[0].set_ylabel('Score')
    ax[0].title.set_text('Elbow Curve')

    ax[1].scatter(pca_d[:, 0], pca_d[:, 1], c = labels)
    ax[1].set_xlabel('')
    ax[1].set_ylabel('')
    ax[1].title.set_text('Cluster K-Means')

    fig.tight_layout(h_pad=2)

    return fig

@app.route('/wordcloud')
def plot_wc():
    clust = Clusters(final_df) 
    labels, Nc, score, pca_d, = clust.segmentation()
    clouds = clust.wordcloud()

    fig_2 = create_figure_2(clouds)
    output_2 = io.BytesIO()

    FigureCanvas(fig_2).print_png(output_2)
    return Response(output_2.getvalue(), mimetype='image/png')

def create_figure_2(clouds):
    
    n = len(clouds)
    fig, ax = plt.subplots(n)

    for i in range(n):
        ax[i].imshow(clouds[i])
        ax[i].axis('off')

    fig.tight_layout(h_pad=2)

    return fig


if __name__ == "__main__":
    Timer(1, open_browser).start();
    app.run(port=8080)

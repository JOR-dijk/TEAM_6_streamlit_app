import streamlit as st
import plotly.express as px
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
import plotly.graph_objects as go
import plotly.express as px

st.title("overzicht lifestyle coach")


if "naam" in st.session_state:
    st.write(f"Hallo {st.session_state['naam']}!")
else:
    st.write("Nog geen naam opgeslagen.")
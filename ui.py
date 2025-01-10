import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from backend import SearchEngine


data_path = "data/bbc"
dense_llm_model = "nli-bert-large-max-pooling"
# Additional Data
enrich_data_url = None
se = SearchEngine(dense_llm_model, data_path)


def extract_header_body(item):
    item_split = "\n\n".join(item.split("\n\n")[:2])
    item_header, item_body = item_split[:2], item_split[2:]
    return item_header, item_header


def _get_session():

    ctx = get_script_run_ctx()
    session_id = ctx.session_id
    if session_id is None:
        raise RuntimeError("Couldn't get your streamlit session")
    return session_id


def search_app():
    st.title("Search App")
    st.write("Enter a search query to find relevant data:")

    # Input box for the query
    query = st.text_input("Search Query", "")

    if query:
        # Call the search function with the user input
        results = se.search_engine(query)
        if results:
            st.write("### Results:")
            for result in results:
                st.write("- ", result)
        else:
            st.write("No results found for your query.")


if __name__ == "__main__":
    search_app()






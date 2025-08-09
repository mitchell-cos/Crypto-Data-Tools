import os
import json
import pandas as pd
import streamlit as st

# --- Streamlit Page Config & CSS ---
st.set_page_config(page_title="Count On Sheep", layout="centered")
st.markdown("""
<style>
    body, .stApp { background-color: #03444e !important; }
    .block-container { padding-top: 0.5rem !important; }
    .stTabs { margin-top: 0.2rem !important; }
    h1 { margin-top: 0.1rem !important; margin-bottom: 0.1rem !important; color: #96c83f !important; }
    h4 { margin-top: 0 !important; margin-bottom: 0.1rem !important; }
</style>
""", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center;">
    <h1>Count On Sheep</h1>
    <h4>Tax Tools</h4>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Scripts", "Explorers", "Tools", "Templates"])

# --- Tab 1: Run Script on Uploaded File ---
with tab1:
    st.write("### Run Script on Uploaded File")
    scripts_dir = os.path.join(os.getcwd(), "Scripts")
    script_files = [f for f in os.listdir(scripts_dir) if f.endswith('.py')] if os.path.exists(scripts_dir) else []
    selected_script = st.selectbox("Select a script", script_files) if script_files else None
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

    df_input = None
    if uploaded_file:
        try:
            df_input = pd.read_csv(uploaded_file)
            st.write(f"Input Preview (showing {min(len(df_input), 1000)} of {len(df_input)} rows):")
            st.dataframe(df_input.head(1000), height=300)
        except Exception as e:
            st.error(f"Error reading file: {e}")

    if not script_files:
        st.info("Scripts folder not found or no scripts available.")
    elif not uploaded_file:
        st.info("Please upload a file.")
    elif selected_script and df_input is not None:
        if st.button("Execute Script"):
            try:
                with open(os.path.join(scripts_dir, selected_script), encoding="utf-8") as f:
                    ns = {}
                    exec(f.read(), {}, ns)
                process = ns.get("process")
                if callable(process):
                    output = process(df_input.copy())
                    if isinstance(output, pd.DataFrame):
                        st.session_state['last_output'] = output
                    else:
                        st.error("'process' must return a DataFrame.")
                else:
                    st.error("Script must define: process(input_df) -> output_df")
            except Exception as e:
                st.error(f"Error running script: {e}")

    output = st.session_state.get('last_output')
    if isinstance(output, pd.DataFrame):
        st.write(f"Processed Output (showing {min(len(output), 1000)} of {len(output)} rows):")
        st.dataframe(output.head(1000), height=300)
        input_name = os.path.splitext(uploaded_file.name)[0]
        script_name = os.path.splitext(selected_script)[0]
        output_filename = f"{input_name}_{script_name}.csv"
        st.download_button(
            label="Download CSV",
            data=output.to_csv(index=False).encode('utf-8'),
            file_name=output_filename,
            mime="text/csv"
        )

# --- Helpers for JSON Storage ---
def ensure_json(path, default=None):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default if default is not None else {}, f, indent=4)

def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- Tab 2: Block Explorers ---
LINKS_JSON = "block_explorers.json"
ensure_json(LINKS_JSON)

def read_links():
    data = read_json(LINKS_JSON)
    return [{"Name": k, "URL": v} for k, v in data.items()]

def add_link(name, url):
    data = read_json(LINKS_JSON)
    data.pop(name, None)
    data[name] = url
    write_json(LINKS_JSON, dict(sorted(data.items())))

with tab2:
    st.write("### Block Explorers")
    with st.expander("Add New Block Explorer Link", expanded=False):
        with st.form("add_link_form"):
            new_name = st.text_input("Blockchain Name")
            new_url = st.text_input("Explorer URL")
            if st.form_submit_button("Add Link"):
                if new_name and new_url:
                    add_link(new_name, new_url)
                    st.success(f"Added link for {new_name}")
                else:
                    st.error("Please provide both a name and a URL.")

    links = sorted(read_links(), key=lambda x: x["Name"].lower())
    if links:
        num_cols = 5
        rows = [links[i:i+num_cols] for i in range(0, len(links), num_cols)]
        table_html = '<table style="width:100%; text-align:center;">'
        for row in rows:
            table_html += '<tr>' + ''.join(
                f'<td style="padding: 10px;"><a href="{link["URL"]}" target="_blank">{link["Name"]}</a></td>'
                for link in row
            )
            table_html += '<td></td>' * (num_cols - len(row)) + '</tr>'
        table_html += '</table>'
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("No links available yet.")

# --- Tab 3: Tools ---
TOOLS_JSON = "tools.json"
ensure_json(TOOLS_JSON)

def read_tools():
    data = read_json(TOOLS_JSON)
    return [{"Name": k, "URL": v["url"], "Description": v["description"]} for k, v in data.items()]

def add_tool(name, url, description):
    data = read_json(TOOLS_JSON)
    data.pop(name, None)
    data[name] = {"url": url, "description": description}
    write_json(TOOLS_JSON, dict(sorted(data.items())))

with tab3:
    st.write("### Tools")
    with st.expander("Add New Tool", expanded=False):
        with st.form("add_tool_form"):
            tool_name = st.text_input("Tool Name")
            tool_url = st.text_input("Tool Link")
            tool_desc = st.text_area("Description")
            if st.form_submit_button("Add Tool"):
                if tool_name and tool_url and tool_desc:
                    add_tool(tool_name, tool_url, tool_desc)
                    st.success(f"Added tool: {tool_name}")
                else:
                    st.error("Please provide name, link, and description.")

    tools = sorted(read_tools(), key=lambda x: x["Name"].lower())
    if tools:
        table_html = (
            '<table style="width:100%; text-align:left;">'
            "<tr><th style='padding: 8px;'>Tool</th><th style='padding: 8px;'>Description</th></tr>"
        )
        for tool in tools:
            table_html += (
                f"<tr><td style='padding: 8px;'><a href='{tool['URL']}' target='_blank'>{tool['Name']}</a></td>"
                f"<td style='padding: 8px;'>{tool['Description']}</td></tr>"
            )
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("No tools available yet.")

# --- Tab 4: Templates ---
with tab4:
    templates_dir = os.path.join(os.getcwd(), "Templates")
    if os.path.exists(templates_dir):
        repo_files = [f for f in os.listdir(templates_dir)
                      if os.path.isfile(os.path.join(templates_dir, f)) and f.endswith('.csv')]
        for file in repo_files:
            file_path = os.path.join(templates_dir, file)
            with open(file_path, "rb") as f:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(file)
                with col2:
                    st.download_button(label="Download", data=f, file_name=file)

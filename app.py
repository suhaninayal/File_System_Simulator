import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from file_manager import (
    create_file, delete_file, get_all_files, get_file_content,
    update_file_content, get_disk, get_free_block_count
)
from visualization import show_disk, show_disk_access_animation, visualize_file_fragmentation
from process_manager import Process, ProcessManager
from disk_scheduler import (
    fcfs_scheduling, sstf_scheduling, scan_scheduling,
    c_scan_scheduling, look_scheduling, c_look_scheduling,
    visualize_disk_scheduling
)

st.set_page_config(page_title="File System Simulator", layout="wide")

# Initialize session state
if 'process_manager' not in st.session_state:
    st.session_state.process_manager = ProcessManager()
if 'disk_access_history' not in st.session_state:
    st.session_state.disk_access_history = []
if 'file_history' not in st.session_state:
    st.session_state.file_history = [(datetime.now(), 0)]

st.markdown("""
    <h1 style='text-align: center;'>📁 File System Simulator</h1>
    <p style='text-align: center; font-size:18px;'>Visualize how file systems and OS concepts like disk scheduling and process management work.</p>
""", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)


# -------------------- PAGE FUNCTIONS --------------------

def create_file_page():
    st.subheader("📝 Create a New File")
    with st.form("create_file_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            file_name = st.text_input("📁 File Name")
        with col2:
            file_size = st.number_input("📦 File Size (in blocks)", min_value=1, max_value=20, step=1)
        with col3:
            method = st.selectbox("⚙️ Allocation Method", ["Contiguous", "Linked", "Indexed"])

        content = st.text_area("📝 File Content", height=150)

        submitted = st.form_submit_button("➕ Create File", use_container_width=True)
        if submitted:
            if file_name and create_file(file_name, file_size, method, 'Text', content):
                st.success(f"✅ File '{file_name}' created using **{method}** allocation.")

                # Track disk usage history
                used_blocks = len(get_disk()) - get_free_block_count()
                st.session_state.file_history.append((datetime.now(), used_blocks))

                # Add disk access operation to history
                st.session_state.disk_access_history.append(
                    {"operation": "create", "file": file_name, "size": file_size, "time": datetime.now()}
                )
            else:
                st.error("❌ File creation failed. Check for name duplication or space issues.")


def view_files_page():
    st.subheader("📄 File Directory")
    file_data = get_all_files()

    # Show total disk usage stats
    total_blocks = len(get_disk())
    used_blocks = total_blocks - get_free_block_count()
    usage_percent = (used_blocks / total_blocks) * 100 if total_blocks > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Blocks", total_blocks)
    col2.metric("Used Blocks", used_blocks)
    col3.metric("Usage", f"{usage_percent:.1f}%")

    st.markdown("---")

    if file_data:
        # Create a dataframe for better display
        file_list = []
        for name, info in file_data.items():
            file_list.append({
                "Name": name,
                "Size (blocks)": info['size'],
                "Method": info['method'],
                "Blocks": str(info['blocks']),
                "Created": info.get('created_at', 'Unknown'),
                "Modified": info.get('last_modified', 'Unknown')
            })

        if file_list:
            df = pd.DataFrame(file_list)
            st.dataframe(df, use_container_width=True)

        for name, info in file_data.items():
            with st.expander(f"📂 {name} | Method: {info['method']}", expanded=False):
                st.markdown(f"""
                    <ul>
                        <li><strong>Size:</strong> {info['size']} blocks</li>
                        <li><strong>Allocated Blocks:</strong> {info['blocks']}</li>
                        {'<li><strong>Index Block:</strong> ' + str(info['index']) + '</li>' if info['method'] == 'Indexed' else ''}
                        <li><strong>Created:</strong> {info.get('created_at', 'Unknown')}</li>
                        <li><strong>Last Modified:</strong> {info.get('last_modified', 'Unknown')}</li>
                    </ul>
                """, unsafe_allow_html=True)
                st.code(info['content'], language='text')
    else:
        st.info("🪶 No files created yet.")


def edit_file_page():
    st.subheader("✏️ Edit File Content")
    editable_files = list(get_all_files().keys())
    if editable_files:
        file_to_edit = st.selectbox("Select a file to edit", editable_files)
        if file_to_edit:
            current_content = get_file_content(file_to_edit)
            new_content = st.text_area("📝 File Editor", value=current_content, height=200)
            if st.button("💾 Save Changes"):
                update_file_content(file_to_edit, new_content)
                st.success(f"📝 Content of '{file_to_edit}' updated.")

                # Add to disk access history
                st.session_state.disk_access_history.append(
                    {"operation": "update", "file": file_to_edit, "time": datetime.now()}
                )
    else:
        st.info("📂 No files available to edit.")


def delete_file_page():
    st.subheader("🗑️ Delete Files")
    file_list = list(get_all_files().keys())
    if file_list:
        selected_files = st.multiselect("Select files to delete", file_list)
        if st.button("🧺 Delete Selected", use_container_width=True):
            for f in selected_files:
                delete_file(f)

                # Add to disk access history
                st.session_state.disk_access_history.append(
                    {"operation": "delete", "file": f, "time": datetime.now()}
                )

                # Track disk usage history
                used_blocks = len(get_disk()) - get_free_block_count()
                st.session_state.file_history.append((datetime.now(), used_blocks))

            st.success("✅ Selected files deleted.")
    else:
        st.info("📂 No files currently available for deletion.")


def disk_visualization_page():
    st.subheader("📊 Disk Usage Visualization")

    # Basic disk visualization
    st.markdown("### 🧩 Disk Block Allocation")
    st.markdown("Color-coded chart shows how blocks are allocated.")
    fig = show_disk()
    st.pyplot(fig)

    # File fragmentation visualization
    st.markdown("### 🧬 File Fragmentation Analysis")
    frag_fig = visualize_file_fragmentation()
    if frag_fig:
        st.pyplot(frag_fig)
    else:
        st.info("No files to analyze fragmentation.")


def process_simulation_page():
    st.subheader("🧠 Process Management")

    # Process scheduling algorithm selection
    algorithm = st.radio(
        "⚙️ Process Scheduling Algorithm",
        ["priority", "fcfs", "round_robin", "sjf"],
        horizontal=True
    )

    # Update algorithm if changed
    if st.session_state.process_manager.algorithm != algorithm:
        st.session_state.process_manager.change_algorithm(algorithm)
        st.success(f"Scheduling algorithm changed to {algorithm.upper()}")

    # Add new process form
    with st.form("add_process"):
        col1, col2, col3 = st.columns(3)
        with col1:
            pid = st.text_input("🔢 Process ID")
        with col2:
            action = st.selectbox("⚙️ Action", ["read", "write", "delete"])
        with col3:
            file_options = list(get_all_files().keys())
            file = st.selectbox("📂 Target File", file_options if file_options else ["None"])

        priority = st.slider("⭐ Priority (0=high)", 0, 10, 5)

        if st.form_submit_button("➕ Add Process"):
            if pid and file in get_all_files():
                process = Process(pid, action, file, priority)
                st.session_state.process_manager.add_process(process)
                st.success(f"✅ Process {pid} added with priority {priority}")
            else:
                st.error("❌ Please provide valid process ID and target file")

    # Process queue visualization
    st.markdown("---")
    st.subheader("📝 Process Queue")
    processes = st.session_state.process_manager.list_processes()
    completed_processes = st.session_state.process_manager.list_completed_processes()

    if processes:
        process_data = [{
            "PID": p.pid,
            "Action": p.action,
            "File": p.target_file,
            "Priority": p.priority,
            "Status": p.status
        } for p in processes]
        st.table(process_data)
    else:
        st.info("📭 No processes in queue.")

    # Process execution
    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Execute Next Process", disabled=len(processes) == 0):
            process = st.session_state.process_manager.get_next_process()
            if process:
                st.success(f"✅ Executed: {process.pid} - {process.action} '{process.target_file}'")

    with col2:
        if st.button("🔄 Execute All Processes", disabled=len(processes) == 0):
            executed = 0
            while process := st.session_state.process_manager.get_next_process():
                executed += 1
            st.success(f"✅ Executed {executed} processes")

    # Gantt chart for completed processes
    if completed_processes:
        st.markdown("---")
        st.subheader("📊 Process Execution Timeline")
        gantt_fig = st.session_state.process_manager.visualize_gantt_chart()
        if gantt_fig:
            st.pyplot(gantt_fig)


def disk_scheduling_page():
    st.subheader("📈 Disk Scheduling Algorithms")

    col1, col2 = st.columns(2)

    with col1:
        requests_input = st.text_input("🔢 Enter disk requests (comma separated)", value="10, 5, 20, 35, 15")
        start = st.slider("🎯 Initial Head Position", 0, 49, 10)

    with col2:
        algorithm = st.selectbox(
            "🧮 Algorithm",
            ["FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK"]
        )
        direction = st.radio("Direction", ["Up", "Down"], horizontal=True)

    try:
        requests = [int(r.strip()) for r in requests_input.split(",")]
    except:
        st.error("❌ Invalid input format. Please enter comma-separated numbers.")
        return

    if st.button("▶️ Simulate Scheduling", use_container_width=True):
        dir_param = 'up' if direction == "Up" else 'down'

        # Execute selected algorithm
        if algorithm == "FCFS":
            sequence = fcfs_scheduling(requests.copy(), start)
            fig = visualize_disk_scheduling("FCFS", sequence)
        elif algorithm == "SSTF":
            sequence = sstf_scheduling(requests.copy(), start)
            fig = visualize_disk_scheduling("SSTF", sequence)
        elif algorithm == "SCAN":
            sequence = scan_scheduling(requests.copy(), start, dir_param)
            fig = visualize_disk_scheduling("SCAN", sequence)
        elif algorithm == "C-SCAN":
            sequence = c_scan_scheduling(requests.copy(), start)
            fig = visualize_disk_scheduling("C-SCAN", sequence)
        elif algorithm == "LOOK":
            sequence = look_scheduling(requests.copy(), start, dir_param)
            fig = visualize_disk_scheduling("LOOK", sequence)
        elif algorithm == "C-LOOK":
            sequence = c_look_scheduling(requests.copy(), start)
            fig = visualize_disk_scheduling("C-LOOK", sequence)

        # Calculate total movement
        if len(sequence) > 1:
            movement = sum(abs(sequence[i] - sequence[i - 1]) for i in range(1, len(sequence)))

            # Display results
            st.markdown(f"### Results for {algorithm}")
            st.markdown(f"**Head Movement Sequence:** {sequence}")
            st.markdown(f"**Total Head Movement:** {movement} cylinders")

            # Show visualization
            st.pyplot(fig)

            # Show animated visualization
            st.markdown("### 🎬 Animated Head Movement")
            anim_fig = show_disk_access_animation(sequence)
            st.pyplot(anim_fig)

            # Save to history
            st.session_state.disk_access_history.append({
                "algorithm": algorithm,
                "sequence": sequence,
                "total_movement": movement,
                "time": datetime.now()
            })


# -------------------- MAIN --------------------

def main():
    pages = [
        "Create File", "View Files", "Edit File", "Delete File", "Process Simulation", "Disk Scheduling",
        "Disk Visualization"
    ]
    selected_page = st.sidebar.radio("📚 Select a Page", pages)

    if selected_page == "Create File":
        create_file_page()
    elif selected_page == "View Files":
        view_files_page()
    elif selected_page == "Edit File":
        edit_file_page()
    elif selected_page == "Delete File":
        delete_file_page()
    elif selected_page == "Process Simulation":
        process_simulation_page()
    elif selected_page == "Disk Scheduling":
        disk_scheduling_page()
    elif selected_page == "Disk Visualization":
        disk_visualization_page()


if __name__ == "__main__":
    main()

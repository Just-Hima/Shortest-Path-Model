import pandas as pd
import json
import time
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox
from tabulate import tabulate  # Add this import
from fpdf import FPDF  # Add this import
import os  # Add this import


def read_file(file_path):
    """Detect and read data from CSV, XLSX, or JSON file."""
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        data = pd.read_excel(file_path)
    elif file_path.endswith('.json'):
        with open(file_path, 'r') as f:
            data = pd.DataFrame(json.load(f))
    else:
        raise ValueError("Unsupported file format. Use CSV, XLSX, or JSON.")
    return data


def build_graph(data):
    """Build a graph from the DataFrame."""
    G = nx.DiGraph()
    for _, row in data.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    return G


def solve_shortest_path(graph, start_node, end_node):
    """Solve the shortest path problem using Dijkstra's algorithm."""
    start_time = time.time()
    try:
        path = nx.dijkstra_path(graph, source=start_node, target=end_node, weight='weight')
        cost = nx.dijkstra_path_length(graph, source=start_node, target=end_node, weight='weight')
    except nx.NetworkXNoPath:
        raise ValueError(f"No path found between {start_node} and {end_node}.")
    end_time = time.time()
    computation_time = (end_time - start_time) * 1000 
    return path, cost, computation_time


def solve_all_pairs_shortest_paths(graph):
    """Solve the shortest path problem for all pairs using Floyd-Warshall algorithm."""
    start_time = time.time()
    try:
        path_lengths = dict(nx.floyd_warshall(graph, weight='weight'))
    except Exception as e:
        raise ValueError(f"An error occurred while calculating all pairs shortest paths: {e}")
    end_time = time.time()
    computation_time = (end_time - start_time) * 1000  
    return path_lengths, computation_time


def draw_graph(graph, path=None):
    """Visualize the graph and highlight the shortest path if provided."""
    pos = nx.planar_layout(graph)  # Planar layout to avoid edge intersections

    plt.figure(figsize=(10, 8))
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', edge_color='gray', 
            node_size=2000, font_size=12, alpha=0.7, width=2)  # Increase node_size
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    if path:
        path_edges = list(zip(path, path[1:]))

        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='red', width=2.5)
    
    plt.title("Graph Visualization")
    plt.axis('off')  # Hide axis for better visualization
    return plt.gcf()  # Return the figure


def generate_report(path, cost, computation_time, graph, report_message):
    """Generate a detailed report of the solution."""
    report = {
        "Shortest Path": path,
        "Total Cost": cost,
        "Computation Time (milliseconds)": computation_time
    }
    # Show the report message with the graph diagram
    full_report_message = "\n".join([f"{key}: {value}" for key, value in report.items()])
    full_report_message += "\n\n" + report_message

    return full_report_message


def generate_report_all_pairs(path_lengths, computation_time, graph, report_message):
    """Generate a detailed report of the all-pairs shortest paths solution."""
    report = {
        "Computation Time (milliseconds)": computation_time
    }
    # Format the path lengths for better readability
    formatted_paths = {}
    for source, targets in path_lengths.items():
        formatted_paths[source] = {target: f"{dist:.2f}" if dist != float('inf') else "inf" for target, dist in targets.items()}
    report["All Pairs Shortest Paths"] = formatted_paths

    # Create a DataFrame for the path lengths
    nodes = list(path_lengths.keys())
    table_data = {source: [formatted_paths[source][target] for target in nodes] for source in nodes}
    df = pd.DataFrame(table_data, index=nodes)

    # Convert the DataFrame to a formatted table using tabulate
    table = tabulate(df, headers='keys', tablefmt='plain')

    # Show the report message with the graph diagram
    full_report_message = f"Computation Time (milliseconds): {computation_time}\n\n{table}\n\n{report_message}"

    return full_report_message


def generate_text_report_all_pairs(path_lengths, computation_time, graph, report_message):
    """Generate a plain text report of the all-pairs shortest paths solution."""
    report = {
        "Computation Time (milliseconds)": computation_time
    }
    # Format the path lengths for better readability
    formatted_paths = {}
    for source, targets in path_lengths.items():
        formatted_paths[source] = {target: f"{dist:.2f}" if dist != float('inf') else "inf" for target, dist in targets.items()}
    report["All Pairs Shortest Paths"] = formatted_paths

    # Create a DataFrame for the path lengths
    nodes = list(path_lengths.keys())
    table_data = {source: [formatted_paths[source][target] for target in nodes] for source in nodes}
    df = pd.DataFrame(table_data, index=nodes)

    # Convert the DataFrame to a formatted table using tabulate
    table = tabulate(df, headers='keys', tablefmt='plain')

    # Generate the full text report
    text_report = (
        f"All Pairs Shortest Paths Report\n"
        f"Computation Time (milliseconds): {computation_time}\n"
        f"{table}\n"
        f"{report_message}\n"
    )
    return text_report


def save_report_to_pdf(report_content, pdf_path, fig=None):
    """Save report content to a PDF file, including a figure if provided."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, report_content)
    
    if fig:
        # Save the figure as an image
        fig_path = "temp_figure.png"
        fig.savefig(fig_path, bbox_inches='tight')
        pdf.image(fig_path, x=10, y=None, w=190)  # Adjust the width as needed
        os.remove(fig_path)  # Remove the temporary image file

    pdf.output(pdf_path)


def show_instructions():
    """Display usage instructions with an image in the same window."""
    instructions = (
        "1. Click the 'Import File' button to upload a CSV, XLSX, or JSON file containing the graph data.\n"
        "2. The file should contain the following columns: 'source', 'target', and 'weight'.\n"
        "3. Enter the start and end nodes when prompted.\n"
        "4. The model will solve the shortest path problem and display the result.\n"
        "5. A graph visualization will also be shown.\n\n"
        "You can also manually enter edges using the 'Manual Input' button."
    )

    instructions_window = tk.Toplevel()
    instructions_window.title("How to Use with Image")

    frame = tk.Frame(instructions_window)
    frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

    instructions_label = tk.Label(frame, text=instructions, justify=tk.LEFT, font=("Helvetica", 16))
    instructions_label.pack(pady=10, expand=True)

    img = tk.PhotoImage(file= r"files/img/info.png")  # Ensure this is the correct path
    img_label = tk.Label(frame, image=img)
    img_label.image = img  # Keep a reference to the image to avoid garbage collection
    img_label.pack(pady=10, expand=True)

    instructions_window.mainloop()


def show_frame(frame):
    frame.tkraise()


def delete_edge(edge_listbox):
    selected_items = edge_listbox.curselection()
    for item in selected_items[::-1]:
        edge_listbox.delete(item)

def add_edge(source_entry, target_entry, weight_entry, edge_listbox, event=None):
    source = source_entry.get()
    target = target_entry.get()
    weight = weight_entry.get()

    if source and target and weight:
        edge_listbox.insert(tk.END, f"{source} -> {target} (weight: {weight})")
    
    # Clear the entries and return focus to the source entry
    source_entry.delete(0, tk.END)
    target_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    source_entry.focus_set()

def main_gui():
    """Create the GUI for the model."""
    def import_file():
        file_path = filedialog.askopenfilename(title="Select File", 
                                               filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("JSON files", "*.json")])
        if not file_path:
            return

        try:
            data = read_file(file_path)
            graph = build_graph(data)
            choose_option(graph)

        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def manual_input():
        show_frame(manual_input_frame)

    def solve_manual_input(edge_listbox):
        edges = []
        for item in edge_listbox.get(0, tk.END):
            parts = item.split()
            source = parts[0]
            target = parts[2]
            weight = float(parts[4].strip('()'))
            edges.append((source, target, weight))

        if not edges:
            messagebox.showerror("Error", "No edges provided.")
            return

        G = nx.DiGraph()
        for source, target, weight in edges:
            G.add_edge(source, target, weight=weight)

        choose_option(G)

    def choose_option(graph):
        def get_nodes():
            node_popup = tk.Toplevel(root)
            node_popup.title("Choose Option")
            node_popup.geometry("400x200")
            node_popup.transient(root)
            node_popup.grab_set()

            tk.Label(node_popup, text="Choose an option:", font=("Helvetica", 14)).pack(pady=10)
            tk.Button(node_popup, text="Shortest Path Between Two Points", command=lambda: get_specific_nodes(node_popup, graph), font=("Helvetica", 14)).pack(pady=10)
            tk.Button(node_popup, text="Shortest Path for Whole Network", command=lambda: process_whole_network(node_popup, graph), font=("Helvetica", 14)).pack(pady=10)

        def get_specific_nodes(parent_popup, graph):
            parent_popup.destroy()
            node_popup = tk.Toplevel(root)
            node_popup.title("Enter Nodes")
            node_popup.geometry("400x200")
            node_popup.transient(root)
            node_popup.grab_set()

            tk.Label(node_popup, text="Enter the start node:", font=("Helvetica", 14)).pack(pady=10)
            start_entry = tk.Entry(node_popup, font=("Helvetica", 14))
            start_entry.pack(pady=5)

            tk.Label(node_popup, text="Enter the end node:", font=("Helvetica", 14)).pack(pady=10)
            end_entry = tk.Entry(node_popup, font=("Helvetica", 14))
            end_entry.pack(pady=5)

            def on_submit():
                start_node = start_entry.get()
                end_node = end_entry.get()
                if not start_node or not end_node:
                    messagebox.showerror("Error", "Please enter both start and end nodes.")
                    return
                node_popup.destroy()
                process_graph(graph, start_node, end_node)

            start_entry.bind("<Return>", lambda event: end_entry.focus_set())
            end_entry.bind("<Return>", lambda event: on_submit())

            tk.Button(node_popup, text="Submit", command=on_submit, font=("Helvetica", 14)).pack(pady=20)

        def process_whole_network(parent_popup, graph):
            parent_popup.destroy()
            try:
                path_lengths, computation_time = solve_all_pairs_shortest_paths(graph)
                report_message = "The shortest paths for the whole network have been calculated."
                report_content = generate_report_all_pairs(path_lengths, computation_time, graph, report_message)

                # Save the report as a PDF file
                solutions_dir = "Solutions"
                os.makedirs(solutions_dir, exist_ok=True)
                pdf_path = os.path.join(solutions_dir, "all_pairs_shortest_paths_report.pdf")
                save_report_to_pdf(report_content, pdf_path)

                result_popup = tk.Toplevel()
                result_popup.title("Result")
                result_popup.geometry("1100x800")
                result_popup.transient(root)
                result_popup.grab_set()

                frame = tk.Frame(result_popup)
                frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

                report_label = tk.Label(frame, text=report_content, font=("Helvetica", 16))
                report_label.pack(pady=20, expand=True, fill=tk.BOTH)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

        def process_graph(graph, start_node, end_node):
            try:
                path, cost, computation_time = solve_shortest_path(graph, start_node, end_node)

                fig = draw_graph(graph, path)
                report_message = "The diagram will be displayed below with the result."
                report_content = generate_report(path, cost, computation_time, graph, report_message)

                # Save the report as a PDF file
                solutions_dir = "Solutions"
                os.makedirs(solutions_dir, exist_ok=True)
                pdf_path = os.path.join(solutions_dir, "shortest_path_report.pdf")
                save_report_to_pdf(report_content, pdf_path, fig)

                result_popup = tk.Toplevel()
                result_popup.title("Result")
                result_popup.geometry("1100x800")
                result_popup.transient(root)
                result_popup.grab_set()

                frame = tk.Frame(result_popup)
                frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

                report_label = tk.Label(frame, text=report_content, font=("Helvetica", 16))
                report_label.pack(pady=20, expand=True, fill=tk.BOTH)

                canvas = FigureCanvasTkAgg(fig, master=frame)
                canvas.draw()
                canvas.get_tk_widget().pack(pady=10, expand=True, fill=tk.BOTH)

            except ValueError as ve:
                messagebox.showerror("Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

        get_nodes()

    def show_instructions():
        show_frame(instructions_frame)

    root = tk.Tk()
    root.title("Shortest Path Model")
    root.geometry("1100x800")

    main_frame = tk.Frame(root)
    manual_input_frame = tk.Frame(root)
    instructions_frame = tk.Frame(root)
    result_frame = tk.Frame(root)

    for frame in (main_frame, manual_input_frame, instructions_frame, result_frame):
        frame.grid(row=0, column=0, sticky='nsew')

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Main Frame
    main_frame_content = tk.Frame(main_frame)
    main_frame_content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    tk.Label(main_frame_content, text="Shortest Path Model", font=("Helvetica", 20)).pack(pady=20)
    tk.Button(main_frame_content, text="Import File", command=import_file, font=("Helvetica", 16), width=20).pack(pady=10)
    tk.Button(main_frame_content, text="Manual Input", command=manual_input, font=("Helvetica", 16), width=20).pack(pady=10)
    tk.Button(main_frame_content, text="Instructions", command=show_instructions, font=("Helvetica", 16), width=20).pack(pady=10)

    main_frame_content.grid(row=0, column=0, sticky='nsew')
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    # Manual Input Frame
    manual_input_content = tk.Frame(manual_input_frame)
    manual_input_content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    tk.Label(manual_input_content, text="Manual Input", font=("Helvetica", 20)).pack(pady=20)
    frame = tk.Frame(manual_input_content)
    frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

    tk.Label(frame, text="Source Node", font=("Helvetica", 16)).pack(pady=5, anchor=tk.CENTER)
    source_entry = tk.Entry(frame, font=("Helvetica", 16))
    source_entry.pack(pady=5, anchor=tk.CENTER)

    tk.Label(frame, text="Target Node", font=("Helvetica", 16)).pack(pady=5, anchor=tk.CENTER)
    target_entry = tk.Entry(frame, font=("Helvetica", 16))
    target_entry.pack(pady=5, anchor=tk.CENTER)

    tk.Label(frame, text="Weight", font=("Helvetica", 16)).pack(pady=5, anchor=tk.CENTER)
    weight_entry = tk.Entry(frame, font=("Helvetica", 16))
    weight_entry.pack(pady=5, anchor=tk.CENTER)

    edge_listbox = tk.Listbox(frame, font=("Helvetica", 16), height=10, width=30)
    edge_listbox.pack(pady=5, anchor=tk.CENTER)

    tk.Button(frame, text="Add Edge", command=lambda: add_edge(source_entry, target_entry, weight_entry, edge_listbox), font=("Helvetica", 16)).pack(pady=5, anchor=tk.CENTER)
    tk.Button(frame, text="Delete Edge", command=lambda: delete_edge(edge_listbox), font=("Helvetica", 16)).pack(pady=5, anchor=tk.CENTER)
    tk.Button(frame, text="Clear All", command=lambda: edge_listbox.delete(0, tk.END), font=("Helvetica", 16)).pack(pady=5, anchor=tk.CENTER)
    tk.Button(frame, text="Solve", command=lambda: solve_manual_input(edge_listbox), font=("Helvetica", 16)).pack(pady=5, anchor=tk.CENTER)

    source_entry.bind("<Return>", lambda event: target_entry.focus_set())
    target_entry.bind("<Return>", lambda event: weight_entry.focus_set())
    weight_entry.bind("<Return>", lambda event: [add_edge(source_entry, target_entry, weight_entry, edge_listbox), source_entry.focus_set()])

    manual_input_content.grid(row=0, column=0, sticky='nsew')
    manual_input_frame.grid_rowconfigure(0, weight=1)
    manual_input_frame.grid_columnconfigure(0, weight=1)

    tk.Button(manual_input_frame, text="Back", command=lambda: show_frame(main_frame), font=("Helvetica", 16)).place(relx=1.0, rely=1.0, anchor=tk.SE, x=-10, y=-10)

    # Instructions Frame
    instructions_content = tk.Frame(instructions_frame)
    instructions_content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    tk.Label(instructions_content, text="Instructions", font=("Helvetica", 20)).pack(pady=20)
    frame = tk.Frame(instructions_content)
    frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

    instructions = (
        "1. Click the 'Import File' button to upload a CSV, XLSX, or JSON file containing the graph data.\n"
        "2. The file should contain the following columns: 'source', 'target', and 'weight'.\n"
        "3. Enter the start and end nodes when prompted.\n"
        "4. The model will solve the shortest path problem and display the result.\n"
        "5. A graph visualization will also be shown.\n\n"
        "You can also manually enter edges using the 'Manual Input' button."
    )

    instructions_label = tk.Label(frame, text=instructions, justify=tk.LEFT, font=("Helvetica", 16))
    instructions_label.pack(pady=10, anchor=tk.CENTER, expand=True, fill=tk.BOTH)

    img = tk.PhotoImage(file= r"files/img/info.png")  # Ensure this is the correct path
    img_label = tk.Label(frame, image=img)
    img_label.image = img  # Keep a reference to the image to avoid garbage collection
    img_label.pack(pady=10, anchor=tk.CENTER, expand=True, fill=tk.BOTH)

    instructions_content.grid(row=0, column=0, sticky='nsew')
    instructions_frame.grid_rowconfigure(0, weight=1)
    instructions_frame.grid_columnconfigure(0, weight=1)

    tk.Button(instructions_frame, text="Back", command=lambda: show_frame(main_frame), font=("Helvetica", 16)).place(relx=1.0, rely=1.0, anchor=tk.SE, x=-10, y=-10)

    show_frame(main_frame)
    root.mainloop()

if __name__ == "__main__":
    main_gui()
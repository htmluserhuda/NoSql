import tkinter as tk
from tkinter import ttk
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes App")
        self.root.geometry("400x600")
        self.root.configure(bg="#1A1A1A")

        # MongoDB Connection
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["notes_app"]
        self.notes_collection = self.db["notes"]

        self.additional_properties = {}  # Store custom properties
        self.initialize_main_page()

    def initialize_main_page(self):
        # Clear frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        title = tk.Label(self.root, text="Notes", font=("Helvetica", 24), bg="#1A1A1A", fg="#FFFFFF")
        title.pack(pady=20)

        # Notes list
        notes = self.notes_collection.find()  # Fetch notes from MongoDB
        for note in notes:
            note_frame = tk.Frame(self.root, bg="#F2A900", height=80, bd=5, relief=tk.RIDGE)
            note_frame.pack(fill="x", padx=10, pady=5)

            # Display note details
            tk.Label(note_frame, text=note["title"], font=("Helvetica", 14), bg="#F2A900", fg="#1A1A1A").pack(anchor="w")
            tk.Label(note_frame, text=note["content"], font=("Helvetica", 10), bg="#F2A900", fg="#1A1A1A").pack(anchor="w")
            tk.Label(note_frame, text=note["date"], font=("Helvetica", 8), bg="#F2A900", fg="#1A1A1A").pack(anchor="e")

            # Display additional properties if any
            for key, value in note.get("properties", {}).items():
                tk.Label(note_frame, text=f"{key}: {value}", font=("Helvetica", 10), bg="#F2A900", fg="#1A1A1A").pack(anchor="w")

            # Add Remove Button
            remove_button = tk.Button(note_frame, text="Remove", bg="#FF4C4C", fg="#FFFFFF",
                                       command=lambda note_id=note["_id"]: self.remove_note(note_id))
            remove_button.pack(side="right", padx=5, pady=5)

            # Add Edit Button
            edit_button = tk.Button(note_frame, text="Edit", bg="#00CCFF", fg="#FFFFFF",
                                     command=lambda note=note: self.open_edit_note_window(note))
            edit_button.pack(side="right", padx=5, pady=5)

        # Add button
        add_button = tk.Button(self.root, text="+", bg="#00FFCC", fg="#1A1A1A", font=("Helvetica", 18),
                               command=self.initialize_add_note_page)
        add_button.pack(side="bottom", pady=10)

    def initialize_add_note_page(self):
        # Clear frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        tk.Label(self.root, text="Add Note", font=("Helvetica", 24), bg="#1A1A1A", fg="#FFFFFF").pack(pady=20)

        # Title field
        title_label = tk.Label(self.root, text="Title", bg="#1A1A1A", fg="#00FFCC")
        title_label.pack(anchor="w", padx=20)
        title_entry = tk.Entry(self.root, font=("Helvetica", 14))
        title_entry.pack(fill="x", padx=20)

        # Content field
        content_label = tk.Label(self.root, text="Content", bg="#1A1A1A", fg="#00FFCC")
        content_label.pack(anchor="w", padx=20, pady=10)
        content_entry = tk.Text(self.root, height=5, font=("Helvetica", 14))
        content_entry.pack(fill="x", padx=20)

        # Add Property Button
        add_property_button = tk.Button(self.root, text="Add Property", bg="#F2A900", fg="#1A1A1A",
                                        command=self.open_add_property_window)
        add_property_button.pack(pady=10)

        # Buttons
        tk.Button(self.root, text="Add Note", bg="#00FFCC", fg="#1A1A1A", font=("Helvetica", 14),
                  command=lambda: self.add_note(title_entry.get(), content_entry.get("1.0", tk.END).strip())).pack(
            pady=10)
        tk.Button(self.root, text="Back", bg="#F2A900", fg="#1A1A1A", font=("Helvetica", 14),
                  command=self.initialize_main_page).pack(pady=10)

    def open_add_property_window(self):
        # Create a new window for adding a property
        property_window = tk.Toplevel(self.root)
        property_window.title("Add Property")
        property_window.geometry("300x200")
        property_window.configure(bg="#1A1A1A")

        # Property Name
        tk.Label(property_window, text="Property Name", bg="#1A1A1A", fg="#FFFFFF").pack(pady=10)
        property_name_entry = tk.Entry(property_window, font=("Helvetica", 12))
        property_name_entry.pack(fill="x", padx=20)

        # Property Value
        tk.Label(property_window, text="Property Value", bg="#1A1A1A", fg="#FFFFFF").pack(pady=10)
        property_value_entry = tk.Entry(property_window, font=("Helvetica", 12))
        property_value_entry.pack(fill="x", padx=20)

        # Save Property Button
        save_property_button = tk.Button(property_window, text="Save Property", bg="#00FFCC", fg="#1A1A1A",
                                         command=lambda: self.save_property(property_name_entry.get(),
                                                                             property_value_entry.get(),
                                                                             property_window))
        save_property_button.pack(pady=20)

    def save_property(self, name, value, window):
        # Save the property to the additional properties dictionary
        if name and value:
            self.additional_properties[name] = value
            print(f"Saved property: {name} -> {value}")  # Debugging message
            window.destroy()  # Close the property window

    def add_note(self, title, content):
        if title and content:
            note = {
                "title": title,
                "content": content,
                "date": datetime.now().strftime("%b %d, %Y"),
                "properties": self.additional_properties  # Include custom properties
            }
            self.notes_collection.insert_one(note)  # Save note to MongoDB
        self.additional_properties = {}  # Reset properties for the next note
        self.initialize_main_page()

    def remove_note(self, note_id):
        # Remove note from MongoDB
        self.notes_collection.delete_one({"_id": note_id})
        print(f"Note with ID {note_id} removed!")  # Debugging message
        self.initialize_main_page()  # Refresh the notes list

    def open_edit_note_window(self, note):
        # Create a new window for editing the note
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Note")
        edit_window.geometry("400x400")
        edit_window.configure(bg="#1A1A1A")

        # Title field
        tk.Label(edit_window, text="Edit Title", bg="#1A1A1A", fg="#FFFFFF").pack(pady=10)
        title_entry = tk.Entry(edit_window, font=("Helvetica", 12))
        title_entry.insert(0, note["title"])
        title_entry.pack(fill="x", padx=20)

        # Content field
        tk.Label(edit_window, text="Edit Content", bg="#1A1A1A", fg="#FFFFFF").pack(pady=10)
        content_entry = tk.Text(edit_window, height=5, font=("Helvetica", 12))
        content_entry.insert("1.0", note["content"])
        content_entry.pack(fill="x", padx=20)

        # Additional properties
        tk.Label(edit_window, text="Edit Properties", bg="#1A1A1A", fg="#FFFFFF").pack(pady=10)
        property_entries = {}
        for key, value in note.get("properties", {}).items():
            frame = tk.Frame(edit_window, bg="#1A1A1A")
            frame.pack(fill="x", padx=20, pady=5)

            tk.Label(frame, text=f"{key}", bg="#1A1A1A", fg="#FFFFFF").pack(side="left", padx=5)
            entry = tk.Entry(frame, font=("Helvetica", 12))
            entry.insert(0, value)
            entry.pack(side="left", fill="x", expand=True)
            property_entries[key] = entry

        # Save button
        tk.Button(edit_window, text="Save Changes", bg="#00FFCC", fg="#1A1A1A",
                  command=lambda: self.save_edited_note(note["_id"], title_entry.get(),
                                                        content_entry.get("1.0", tk.END).strip(),
                                                        property_entries, edit_window)).pack(pady=20)

    def save_edited_note(self, note_id, title, content, property_entries, window):
        # Update the note in MongoDB
        updated_properties = {key: entry.get() for key, entry in property_entries.items()}
        self.notes_collection.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": {"title": title, "content": content, "properties": updated_properties}}
        )
        print(f"Note with ID {note_id} updated!")  # Debugging message
        window.destroy()  # Close the edit window
        self.initialize_main_page()  # Refresh the notes list


if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()

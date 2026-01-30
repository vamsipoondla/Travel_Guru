#!/usr/bin/env python3
"""
EU Flight Compensation Claim Generator

A GUI application for generating compensation claim emails under
EC261/2004 (EU) and similar regulations.

Features:
- Flight data lookup via API or manual entry
- Compensation eligibility calculation
- Professional email generation
- Multiple passengers support
- Various claim types (delay, cancellation, denied boarding)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime, timedelta
from typing import Optional, List
import pyperclip
import webbrowser

from config import get_config
from compensation_calculator import (
    FlightDetails, Airport, ClaimType, CompensationResult,
    calculate_compensation, get_airport, is_carrier_eu_based,
    calculate_distance_km, AIRPORT_DATA
)
from flight_service import (
    FlightService, create_flight_details_manual,
    get_airline_name, get_supported_airports
)
from email_generator import (
    PassengerInfo, BankDetails, ClaimEmailData,
    generate_claim_email, generate_subject_line
)
from airline_contacts import (
    get_airline_contact, format_contact_for_display
)
from validators import (
    validate_flight_number, validate_airport_code, validate_date,
    validate_time, validate_booking_reference, validate_name,
    validate_email, validate_iban, validate_bic_swift,
    validate_date_of_birth
)


class FlightCompensationApp:
    """Main application class for EU Flight Compensation Generator."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("EU Flight Compensation Claim Generator")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Initialize services
        self.flight_service = FlightService()
        self.config = get_config()

        # Data storage
        self.passengers: List[PassengerInfo] = []
        self.flight_details: Optional[FlightDetails] = None
        self.compensation_result: Optional[CompensationResult] = None
        self.generated_email: str = ""

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create the main application widgets."""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.create_flight_tab()
        self.create_passengers_tab()
        self.create_exclusions_tab()
        self.create_bank_tab()
        self.create_preview_tab()

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN
        )
        self.status_bar.pack(fill=tk.X, padx=10, pady=(0, 10))

    def create_flight_tab(self):
        """Create the flight details tab."""
        flight_frame = ttk.Frame(self.notebook)
        self.notebook.add(flight_frame, text="Flight Details")

        # Main container with scrollbar
        canvas = tk.Canvas(flight_frame)
        scrollbar = ttk.Scrollbar(flight_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Booking Information Section
        booking_frame = ttk.LabelFrame(scrollable_frame, text="Booking Information", padding=10)
        booking_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(booking_frame, text="Booking Reference:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.booking_ref_var = tk.StringVar()
        self.booking_ref_entry = ttk.Entry(booking_frame, textvariable=self.booking_ref_var, width=20)
        self.booking_ref_entry.grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(booking_frame, text="Travel Date:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(20, 0))
        self.travel_date_var = tk.StringVar()
        self.travel_date_entry = ttk.Entry(booking_frame, textvariable=self.travel_date_var, width=15)
        self.travel_date_entry.grid(row=0, column=3, sticky=tk.W, pady=2)
        ttk.Label(booking_frame, text="(YYYY-MM-DD)").grid(row=0, column=4, sticky=tk.W, pady=2)

        ttk.Label(booking_frame, text="Flight Number:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.flight_number_var = tk.StringVar()
        self.flight_number_entry = ttk.Entry(booking_frame, textvariable=self.flight_number_var, width=15)
        self.flight_number_entry.grid(row=1, column=1, sticky=tk.W, pady=2)

        # API lookup button
        self.lookup_btn = ttk.Button(
            booking_frame, text="Look Up Flight", command=self.lookup_flight
        )
        self.lookup_btn.grid(row=1, column=2, padx=10, pady=2)

        api_status = "API Available" if self.flight_service.has_api_access() else "Manual Entry Mode"
        self.api_status_label = ttk.Label(booking_frame, text=api_status)
        self.api_status_label.grid(row=1, column=3, columnspan=2, sticky=tk.W)

        # Claim Type Section
        claim_frame = ttk.LabelFrame(scrollable_frame, text="Claim Type", padding=10)
        claim_frame.pack(fill=tk.X, padx=10, pady=5)

        self.claim_type_var = tk.StringVar(value="delay")
        claim_types = [
            ("Flight Delay (3+ hours)", "delay"),
            ("Flight Cancellation", "cancellation"),
            ("Denied Boarding", "denied_boarding"),
            ("Missed Connection", "missed_connection"),
        ]

        for i, (text, value) in enumerate(claim_types):
            ttk.Radiobutton(
                claim_frame, text=text, variable=self.claim_type_var, value=value
            ).grid(row=0, column=i, padx=10, sticky=tk.W)

        # Flight Details Section (Manual Entry)
        details_frame = ttk.LabelFrame(scrollable_frame, text="Flight Details", padding=10)
        details_frame.pack(fill=tk.X, padx=10, pady=5)

        # Departure
        ttk.Label(details_frame, text="Departure Airport:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.dep_code_var = tk.StringVar()
        self.dep_code_combo = ttk.Combobox(
            details_frame, textvariable=self.dep_code_var, width=8
        )
        self.dep_code_combo['values'] = [code for code, _, _ in get_supported_airports()]
        self.dep_code_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        self.dep_code_combo.bind('<<ComboboxSelected>>', self.on_airport_selected)

        self.dep_name_var = tk.StringVar()
        self.dep_name_label = ttk.Label(details_frame, textvariable=self.dep_name_var, width=40)
        self.dep_name_label.grid(row=0, column=2, columnspan=2, sticky=tk.W, pady=2)

        # Arrival
        ttk.Label(details_frame, text="Arrival Airport:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.arr_code_var = tk.StringVar()
        self.arr_code_combo = ttk.Combobox(
            details_frame, textvariable=self.arr_code_var, width=8
        )
        self.arr_code_combo['values'] = [code for code, _, _ in get_supported_airports()]
        self.arr_code_combo.grid(row=1, column=1, sticky=tk.W, pady=2)
        self.arr_code_combo.bind('<<ComboboxSelected>>', self.on_airport_selected)

        self.arr_name_var = tk.StringVar()
        self.arr_name_label = ttk.Label(details_frame, textvariable=self.arr_name_var, width=40)
        self.arr_name_label.grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=2)

        # Scheduled times
        ttk.Label(details_frame, text="Scheduled Departure:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.sched_dep_time_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.sched_dep_time_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        ttk.Label(details_frame, text="(HH:MM)").grid(row=2, column=2, sticky=tk.W, pady=2)

        ttk.Label(details_frame, text="Scheduled Arrival:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.sched_arr_time_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.sched_arr_time_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=2)
        ttk.Label(details_frame, text="(HH:MM)").grid(row=3, column=2, sticky=tk.W, pady=2)

        # Actual times
        ttk.Label(details_frame, text="Actual Departure:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.actual_dep_time_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.actual_dep_time_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=2)
        ttk.Label(details_frame, text="(HH:MM, leave blank if cancelled)").grid(row=4, column=2, columnspan=2, sticky=tk.W, pady=2)

        ttk.Label(details_frame, text="Actual Arrival:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.actual_arr_time_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.actual_arr_time_var, width=10).grid(row=5, column=1, sticky=tk.W, pady=2)

        self.next_day_var = tk.BooleanVar()
        ttk.Checkbutton(
            details_frame, text="Arrived next day", variable=self.next_day_var
        ).grid(row=5, column=2, sticky=tk.W, pady=2)

        # Airline info
        ttk.Label(details_frame, text="Airline:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.airline_name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.airline_name_var, width=30).grid(row=6, column=1, columnspan=2, sticky=tk.W, pady=2)

        self.eu_carrier_var = tk.BooleanVar()
        ttk.Checkbutton(
            details_frame, text="EU-based carrier", variable=self.eu_carrier_var
        ).grid(row=6, column=3, sticky=tk.W, pady=2)

        # Calculate button
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.calculate_btn = ttk.Button(
            btn_frame, text="Calculate Compensation", command=self.calculate_compensation
        )
        self.calculate_btn.pack(side=tk.LEFT, padx=5)

        self.view_airline_btn = ttk.Button(
            btn_frame, text="View Airline Contact", command=self.show_airline_contact
        )
        self.view_airline_btn.pack(side=tk.LEFT, padx=5)

        # Result display
        result_frame = ttk.LabelFrame(scrollable_frame, text="Compensation Result", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.result_text = scrolledtext.ScrolledText(result_frame, height=8, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_passengers_tab(self):
        """Create the passengers tab."""
        passengers_frame = ttk.Frame(self.notebook)
        self.notebook.add(passengers_frame, text="Passengers")

        # Add passenger form
        form_frame = ttk.LabelFrame(passengers_frame, text="Add Passenger", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        # Row 1: Names
        ttk.Label(form_frame, text="First Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.passenger_first_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.passenger_first_var, width=25).grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(form_frame, text="Last Name:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(20, 0))
        self.passenger_last_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.passenger_last_var, width=25).grid(row=0, column=3, sticky=tk.W, pady=2)

        # Row 2: DOB and Email
        ttk.Label(form_frame, text="Date of Birth:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.passenger_dob_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.passenger_dob_var, width=15).grid(row=1, column=1, sticky=tk.W, pady=2)

        ttk.Label(form_frame, text="Email:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(20, 0))
        self.passenger_email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.passenger_email_var, width=30).grid(row=1, column=3, sticky=tk.W, pady=2)

        # Row 3: Phone and Address
        ttk.Label(form_frame, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.passenger_phone_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.passenger_phone_var, width=20).grid(row=2, column=1, sticky=tk.W, pady=2)

        ttk.Label(form_frame, text="Address:").grid(row=2, column=2, sticky=tk.W, pady=2, padx=(20, 0))
        self.passenger_address_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.passenger_address_var, width=40).grid(row=2, column=3, sticky=tk.W, pady=2)

        # Add button
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="Add Passenger", command=self.add_passenger).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_passenger_form).pack(side=tk.LEFT, padx=5)

        # Passengers list
        list_frame = ttk.LabelFrame(passengers_frame, text="Passengers on Booking", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview for passengers
        columns = ('name', 'dob', 'email', 'phone')
        self.passengers_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        self.passengers_tree.heading('name', text='Name')
        self.passengers_tree.heading('dob', text='Date of Birth')
        self.passengers_tree.heading('email', text='Email')
        self.passengers_tree.heading('phone', text='Phone')

        self.passengers_tree.column('name', width=200)
        self.passengers_tree.column('dob', width=100)
        self.passengers_tree.column('email', width=200)
        self.passengers_tree.column('phone', width=150)

        self.passengers_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.passengers_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.passengers_tree.configure(yscrollcommand=tree_scroll.set)

        # Remove button
        remove_frame = ttk.Frame(passengers_frame)
        remove_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(remove_frame, text="Remove Selected", command=self.remove_passenger).pack(side=tk.LEFT)
        self.passenger_count_var = tk.StringVar(value="Total: 0 passengers")
        ttk.Label(remove_frame, textvariable=self.passenger_count_var).pack(side=tk.RIGHT)

    def create_exclusions_tab(self):
        """Create the exclusions screening tab."""
        exclusions_frame = ttk.Frame(self.notebook)
        self.notebook.add(exclusions_frame, text="Exclusions")

        # Information label
        info_text = """
IMPORTANT: Under EC261/2004, airlines may refuse compensation if the delay or cancellation
was caused by "extraordinary circumstances" beyond their control.

Please confirm that the disruption was NOT due to any of the following:
        """
        ttk.Label(exclusions_frame, text=info_text, justify=tk.LEFT).pack(padx=10, pady=10)

        # Exclusion checkboxes
        exclusions_container = ttk.LabelFrame(exclusions_frame, text="Confirm None Apply", padding=10)
        exclusions_container.pack(fill=tk.X, padx=10, pady=5)

        self.not_weather_var = tk.BooleanVar()
        ttk.Checkbutton(
            exclusions_container,
            text="NOT caused by severe weather conditions (storms, fog, snow, volcanic ash)",
            variable=self.not_weather_var
        ).pack(anchor=tk.W, pady=2)

        self.not_atc_var = tk.BooleanVar()
        ttk.Checkbutton(
            exclusions_container,
            text="NOT caused by air traffic control restrictions or airport closure",
            variable=self.not_atc_var
        ).pack(anchor=tk.W, pady=2)

        self.not_security_var = tk.BooleanVar()
        ttk.Checkbutton(
            exclusions_container,
            text="NOT caused by security threats or political instability",
            variable=self.not_security_var
        ).pack(anchor=tk.W, pady=2)

        self.not_strike_var = tk.BooleanVar()
        ttk.Checkbutton(
            exclusions_container,
            text="NOT caused by strikes affecting airport or air traffic control (airline staff strikes may still qualify)",
            variable=self.not_strike_var
        ).pack(anchor=tk.W, pady=2)

        self.not_medical_var = tk.BooleanVar()
        ttk.Checkbutton(
            exclusions_container,
            text="NOT caused by medical emergency on board",
            variable=self.not_medical_var
        ).pack(anchor=tk.W, pady=2)

        self.not_bird_var = tk.BooleanVar()
        ttk.Checkbutton(
            exclusions_container,
            text="NOT caused by bird strike or collision with foreign object",
            variable=self.not_bird_var
        ).pack(anchor=tk.W, pady=2)

        # Warning section
        warning_frame = ttk.LabelFrame(exclusions_frame, text="⚠️ Important Notes", padding=10)
        warning_frame.pack(fill=tk.X, padx=10, pady=10)

        warning_text = """
• Technical problems and crew shortages are generally NOT extraordinary circumstances
• Airlines must prove extraordinary circumstances - the burden of proof is on them
• Even if extraordinary circumstances apply, you may still be entitled to assistance (meals, accommodation)
• If unsure, proceed with your claim - the airline will need to provide evidence

By proceeding, you confirm that to the best of your knowledge, the disruption was
within the airline's control and not caused by any extraordinary circumstances.
        """
        ttk.Label(warning_frame, text=warning_text, justify=tk.LEFT).pack()

        self.confirm_proceed_var = tk.BooleanVar()
        ttk.Checkbutton(
            exclusions_frame,
            text="I confirm the above and wish to proceed with my claim",
            variable=self.confirm_proceed_var
        ).pack(pady=10)

    def create_bank_tab(self):
        """Create the bank details tab."""
        bank_frame = ttk.Frame(self.notebook)
        self.notebook.add(bank_frame, text="Bank Details")

        info_label = ttk.Label(
            bank_frame,
            text="Enter your bank details for compensation payment (optional - can be added later):"
        )
        info_label.pack(padx=10, pady=10)

        form_frame = ttk.LabelFrame(bank_frame, text="Bank Account Details", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(form_frame, text="Account Holder Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.bank_holder_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.bank_holder_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=5)

        ttk.Label(form_frame, text="IBAN:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.bank_iban_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.bank_iban_var, width=40).grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(form_frame, text="BIC/SWIFT:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.bank_bic_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.bank_bic_var, width=15).grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Label(form_frame, text="Bank Name:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.bank_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.bank_name_var, width=40).grid(row=3, column=1, sticky=tk.W, pady=5)

    def create_preview_tab(self):
        """Create the email preview tab."""
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="Generate Email")

        # Generate button
        btn_frame = ttk.Frame(preview_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Generate Claim Email", command=self.generate_email).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save as Text File", command=self.save_email).pack(side=tk.LEFT, padx=5)

        # Email preview
        preview_label_frame = ttk.LabelFrame(preview_frame, text="Email Preview", padding=10)
        preview_label_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.email_preview = scrolledtext.ScrolledText(preview_label_frame, wrap=tk.WORD)
        self.email_preview.pack(fill=tk.BOTH, expand=True)

        # Additional actions
        action_frame = ttk.Frame(preview_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(action_frame, text="Open Airline Website", command=self.open_airline_website).pack(side=tk.LEFT, padx=5)

    # ==================== Event Handlers ====================

    def on_airport_selected(self, event=None):
        """Handle airport selection in combobox."""
        dep_code = self.dep_code_var.get().upper()
        arr_code = self.arr_code_var.get().upper()

        if dep_code:
            airport = get_airport(dep_code)
            if airport:
                self.dep_name_var.set(f"{airport.name} ({airport.country})")
            else:
                self.dep_name_var.set("")

        if arr_code:
            airport = get_airport(arr_code)
            if airport:
                self.arr_name_var.set(f"{airport.name} ({airport.country})")
            else:
                self.arr_name_var.set("")

    def lookup_flight(self):
        """Look up flight details using API."""
        flight_number = self.flight_number_var.get().strip()
        travel_date = self.travel_date_var.get().strip()

        # Validate inputs
        valid, result = validate_flight_number(flight_number)
        if not valid:
            messagebox.showerror("Error", result)
            return

        valid, date_result = validate_date(travel_date)
        if not valid:
            messagebox.showerror("Error", date_result)
            return

        self.status_var.set("Looking up flight...")
        self.root.update()

        try:
            search_date = datetime.strptime(date_result, '%Y-%m-%d')
            result, source = self.flight_service.search_flight(result, search_date)

            if result and source != "manual":
                # Populate fields from API result
                self.dep_code_var.set(result.departure_code)
                self.arr_code_var.set(result.arrival_code)
                self.on_airport_selected()

                if result.scheduled_departure:
                    self.sched_dep_time_var.set(result.scheduled_departure.strftime('%H:%M'))
                if result.scheduled_arrival:
                    self.sched_arr_time_var.set(result.scheduled_arrival.strftime('%H:%M'))
                if result.actual_departure:
                    self.actual_dep_time_var.set(result.actual_departure.strftime('%H:%M'))
                if result.actual_arrival:
                    self.actual_arr_time_var.set(result.actual_arrival.strftime('%H:%M'))

                self.airline_name_var.set(result.airline_name)

                # Check if EU carrier
                if is_carrier_eu_based(result.airline_code):
                    self.eu_carrier_var.set(True)

                self.status_var.set(f"Flight found via {source}")
                messagebox.showinfo("Success", f"Flight details retrieved from {source}")
            else:
                self.status_var.set("Flight not found - please enter manually")
                messagebox.showinfo("Not Found", "Flight not found in database. Please enter details manually.")

        except Exception as e:
            self.status_var.set("Lookup failed")
            messagebox.showerror("Error", f"Failed to look up flight: {str(e)}")

    def calculate_compensation(self):
        """Calculate compensation eligibility."""
        try:
            # Validate required fields
            valid, booking_ref = validate_booking_reference(self.booking_ref_var.get())
            if not valid:
                messagebox.showerror("Error", f"Booking Reference: {booking_ref}")
                return

            valid, travel_date = validate_date(self.travel_date_var.get())
            if not valid:
                messagebox.showerror("Error", f"Travel Date: {travel_date}")
                return

            valid, flight_num = validate_flight_number(self.flight_number_var.get())
            if not valid:
                messagebox.showerror("Error", f"Flight Number: {flight_num}")
                return

            valid, dep_code = validate_airport_code(self.dep_code_var.get())
            if not valid:
                messagebox.showerror("Error", f"Departure Airport: {dep_code}")
                return

            valid, arr_code = validate_airport_code(self.arr_code_var.get())
            if not valid:
                messagebox.showerror("Error", f"Arrival Airport: {arr_code}")
                return

            # Get airports
            dep_airport = get_airport(dep_code)
            arr_airport = get_airport(arr_code)

            if not dep_airport:
                messagebox.showerror("Error", f"Unknown departure airport: {dep_code}")
                return
            if not arr_airport:
                messagebox.showerror("Error", f"Unknown arrival airport: {arr_code}")
                return

            # Parse times
            base_date = datetime.strptime(travel_date, '%Y-%m-%d')

            sched_dep_time = self.sched_dep_time_var.get().strip()
            sched_arr_time = self.sched_arr_time_var.get().strip()

            if not sched_dep_time or not sched_arr_time:
                messagebox.showerror("Error", "Please enter scheduled departure and arrival times")
                return

            try:
                sched_dep = datetime.strptime(f"{travel_date} {sched_dep_time}", '%Y-%m-%d %H:%M')
                sched_arr = datetime.strptime(f"{travel_date} {sched_arr_time}", '%Y-%m-%d %H:%M')

                # Handle overnight flights
                if sched_arr <= sched_dep:
                    sched_arr += timedelta(days=1)

            except ValueError:
                messagebox.showerror("Error", "Invalid time format. Use HH:MM (24-hour)")
                return

            # Parse actual times
            actual_dep = None
            actual_arr = None
            claim_type_str = self.claim_type_var.get()

            if claim_type_str != "cancellation":
                actual_arr_time = self.actual_arr_time_var.get().strip()
                if actual_arr_time:
                    try:
                        actual_arr = datetime.strptime(f"{travel_date} {actual_arr_time}", '%Y-%m-%d %H:%M')
                        if self.next_day_var.get() or actual_arr <= sched_arr:
                            if actual_arr < sched_dep:  # Definitely next day
                                actual_arr += timedelta(days=1)
                    except ValueError:
                        messagebox.showerror("Error", "Invalid actual arrival time format")
                        return

                actual_dep_time = self.actual_dep_time_var.get().strip()
                if actual_dep_time:
                    try:
                        actual_dep = datetime.strptime(f"{travel_date} {actual_dep_time}", '%Y-%m-%d %H:%M')
                    except ValueError:
                        pass  # Optional field

            # Map claim type
            claim_type_map = {
                'delay': ClaimType.DELAY,
                'cancellation': ClaimType.CANCELLATION,
                'denied_boarding': ClaimType.DENIED_BOARDING,
                'missed_connection': ClaimType.MISSED_CONNECTION,
            }
            claim_type = claim_type_map.get(claim_type_str, ClaimType.DELAY)

            # Create flight details
            airline_code = flight_num[:2]
            self.flight_details = FlightDetails(
                flight_number=flight_num,
                airline_code=airline_code,
                airline_name=self.airline_name_var.get() or get_airline_name(airline_code),
                departure_airport=dep_airport,
                arrival_airport=arr_airport,
                scheduled_departure=sched_dep,
                scheduled_arrival=sched_arr,
                actual_departure=actual_dep,
                actual_arrival=actual_arr,
                is_cancelled=(claim_type == ClaimType.CANCELLATION),
                is_eu_carrier=self.eu_carrier_var.get() or is_carrier_eu_based(airline_code)
            )

            # Calculate compensation
            self.compensation_result = calculate_compensation(
                self.flight_details,
                claim_type,
                self.config.claim_years_limit
            )

            # Display result
            self.display_compensation_result()
            self.status_var.set("Compensation calculated")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate compensation: {str(e)}")
            self.status_var.set("Calculation failed")

    def display_compensation_result(self):
        """Display compensation calculation result."""
        if not self.compensation_result:
            return

        result = self.compensation_result

        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        if result.eligible:
            text = f"""✅ ELIGIBLE FOR COMPENSATION

Amount per passenger: €{result.amount}
Distance: {result.distance_km:,} km
Delay: {result.delay_hours:.1f} hours

{result.reason}

Legal Basis: {result.legal_basis}
"""
        else:
            text = f"""❌ NOT ELIGIBLE FOR COMPENSATION

{result.reason}
"""

        if result.warnings:
            text += "\n⚠️ Warnings:\n"
            for warning in result.warnings:
                text += f"• {warning}\n"

        self.result_text.insert(tk.END, text)
        self.result_text.configure(state=tk.DISABLED)

    def add_passenger(self):
        """Add a passenger to the list."""
        first_name = self.passenger_first_var.get().strip()
        last_name = self.passenger_last_var.get().strip()

        # Validate required fields
        valid, result = validate_name(first_name, "First name")
        if not valid:
            messagebox.showerror("Error", result)
            return

        valid, result = validate_name(last_name, "Last name")
        if not valid:
            messagebox.showerror("Error", result)
            return

        # Validate optional fields
        dob = self.passenger_dob_var.get().strip()
        if dob:
            valid, result = validate_date_of_birth(dob)
            if not valid:
                messagebox.showerror("Error", result)
                return
            dob = result

        email = self.passenger_email_var.get().strip()
        if email:
            valid, result = validate_email(email)
            if not valid:
                messagebox.showerror("Error", result)
                return
            email = result

        passenger = PassengerInfo(
            first_name=first_name.title(),
            last_name=last_name.title(),
            date_of_birth=dob or None,
            email=email or None,
            phone=self.passenger_phone_var.get().strip() or None,
            address=self.passenger_address_var.get().strip() or None
        )

        self.passengers.append(passenger)
        self.update_passengers_list()
        self.clear_passenger_form()
        self.status_var.set(f"Added passenger: {passenger.first_name} {passenger.last_name}")

    def remove_passenger(self):
        """Remove selected passenger from list."""
        selection = self.passengers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a passenger to remove")
            return

        item = selection[0]
        index = self.passengers_tree.index(item)

        if 0 <= index < len(self.passengers):
            removed = self.passengers.pop(index)
            self.update_passengers_list()
            self.status_var.set(f"Removed passenger: {removed.first_name} {removed.last_name}")

    def update_passengers_list(self):
        """Update the passengers treeview."""
        self.passengers_tree.delete(*self.passengers_tree.get_children())

        for p in self.passengers:
            self.passengers_tree.insert('', tk.END, values=(
                f"{p.first_name} {p.last_name}",
                p.date_of_birth or "",
                p.email or "",
                p.phone or ""
            ))

        self.passenger_count_var.set(f"Total: {len(self.passengers)} passenger(s)")

    def clear_passenger_form(self):
        """Clear the passenger entry form."""
        self.passenger_first_var.set("")
        self.passenger_last_var.set("")
        self.passenger_dob_var.set("")
        self.passenger_email_var.set("")
        self.passenger_phone_var.set("")
        self.passenger_address_var.set("")

    def show_airline_contact(self):
        """Show airline contact information."""
        flight_num = self.flight_number_var.get().strip()
        if len(flight_num) >= 2:
            airline_code = flight_num[:2].upper()
            contact = get_airline_contact(airline_code)

            if contact:
                info = format_contact_for_display(contact)
                messagebox.showinfo(f"{contact.name} Contact Information", info)
            else:
                messagebox.showinfo("Not Found", f"No contact information found for airline code: {airline_code}")
        else:
            messagebox.showwarning("Warning", "Please enter a flight number first")

    def generate_email(self):
        """Generate the compensation claim email."""
        # Validate prerequisites
        if not self.flight_details:
            messagebox.showerror("Error", "Please calculate compensation first (Flight Details tab)")
            return

        if not self.compensation_result or not self.compensation_result.eligible:
            messagebox.showerror("Error", "Flight is not eligible for compensation")
            return

        if not self.passengers:
            messagebox.showerror("Error", "Please add at least one passenger")
            return

        if not self.confirm_proceed_var.get():
            messagebox.showerror("Error", "Please confirm exclusions on the Exclusions tab")
            return

        # Get bank details (optional)
        bank_details = None
        if self.bank_iban_var.get().strip():
            iban = self.bank_iban_var.get().strip()
            valid, result = validate_iban(iban)
            if not valid:
                messagebox.showerror("Error", f"Bank IBAN: {result}")
                return

            bic = self.bank_bic_var.get().strip()
            if bic:
                valid, bic_result = validate_bic_swift(bic)
                if not valid:
                    messagebox.showerror("Error", f"BIC/SWIFT: {bic_result}")
                    return
                bic = bic_result

            bank_details = BankDetails(
                account_holder=self.bank_holder_var.get().strip() or self.passengers[0].first_name + " " + self.passengers[0].last_name,
                iban=result,
                bic_swift=bic or None,
                bank_name=self.bank_name_var.get().strip() or None
            )

        # Create claim data
        claim_data = ClaimEmailData(
            passengers=self.passengers,
            flight=self.flight_details,
            compensation=self.compensation_result,
            booking_reference=self.booking_ref_var.get().strip().upper(),
            bank_details=bank_details
        )

        # Generate email
        self.generated_email = generate_claim_email(claim_data)

        # Display in preview
        self.email_preview.delete(1.0, tk.END)
        self.email_preview.insert(tk.END, self.generated_email)

        self.status_var.set("Email generated successfully")
        self.notebook.select(4)  # Switch to preview tab

    def copy_to_clipboard(self):
        """Copy generated email to clipboard."""
        if not self.generated_email:
            messagebox.showwarning("Warning", "Please generate an email first")
            return

        try:
            pyperclip.copy(self.generated_email)
            self.status_var.set("Email copied to clipboard")
            messagebox.showinfo("Success", "Email copied to clipboard!")
        except Exception as e:
            # Fallback for systems without pyperclip
            self.root.clipboard_clear()
            self.root.clipboard_append(self.generated_email)
            self.status_var.set("Email copied to clipboard")
            messagebox.showinfo("Success", "Email copied to clipboard!")

    def save_email(self):
        """Save generated email to a text file."""
        if not self.generated_email:
            messagebox.showwarning("Warning", "Please generate an email first")
            return

        # Generate default filename
        flight_num = self.flight_number_var.get().strip() or "claim"
        travel_date = self.travel_date_var.get().strip() or datetime.now().strftime('%Y-%m-%d')
        default_filename = f"compensation_claim_{flight_num}_{travel_date}.txt"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=default_filename
        )

        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.generated_email)
                self.status_var.set(f"Email saved to {filepath}")
                messagebox.showinfo("Success", f"Email saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def open_airline_website(self):
        """Open airline claims website."""
        flight_num = self.flight_number_var.get().strip()
        if len(flight_num) >= 2:
            airline_code = flight_num[:2].upper()
            contact = get_airline_contact(airline_code)

            if contact and contact.claims_url:
                webbrowser.open(contact.claims_url)
                self.status_var.set(f"Opened {contact.name} claims portal")
            else:
                messagebox.showinfo("Not Found", "No claims URL found for this airline")
        else:
            messagebox.showwarning("Warning", "Please enter a flight number first")


def main():
    """Main entry point."""
    root = tk.Tk()

    # Set app icon if available
    try:
        root.iconbitmap('icon.ico')
    except Exception:
        pass

    # Apply theme
    style = ttk.Style()
    if 'clam' in style.theme_names():
        style.theme_use('clam')

    app = FlightCompensationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

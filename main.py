#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UH Kalkulator - Aplikacija za računanje ugljenih hidrata
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty
import sqlite3
import os


class CalculationItem(BoxLayout):
    """Jedan red u kalkulaciji"""
    item_name = StringProperty("")
    item_uh = NumericProperty(0)
    
    def __init__(self, name, uh, callback, **kwargs):
        super().__init__(**kwargs)
        self.item_name = name
        self.item_uh = uh
        self.remove_callback = callback
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 50
        self.padding = [10, 5]
        self.spacing = 10
        
        # Label sa imenom i UH
        label = Label(
            text=f"{name} – {uh:.1f} UH",
            size_hint_x=0.8,
            halign='left',
            valign='middle'
        )
        label.bind(size=label.setter('text_size'))
        
        # Dugme za brisanje
        btn_remove = Button(
            text="✕",
            size_hint_x=0.2,
            background_color=(0.9, 0.3, 0.3, 1)
        )
        btn_remove.bind(on_press=lambda x: self.remove_callback(self))
        
        self.add_widget(label)
        self.add_widget(btn_remove)


class SearchResultItem(Button):
    """Jedan rezultat pretrage"""
    def __init__(self, item_data, callback, **kwargs):
        super().__init__(**kwargs)
        self.item_data = item_data
        self.size_hint_y = None
        self.height = 60
        self.halign = 'left'
        self.valign = 'middle'
        self.padding = [15, 10]
        
        name = item_data['name']
        uh = item_data['carbs_g']
        unit = item_data['unit']
        
        self.text = f"{name}\n{uh:.1f}g UH po {unit}"
        self.bind(on_press=lambda x: callback(item_data))


class UHKalkulatorApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_path = "data/items.db"
        self.calculation_items = []  # Lista trenutnih stavki
        self.total_uh = 0
        
    def build(self):
        """Kreira UI"""
        self.title = "UH Kalkulator"
        
        # Glavni layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 1. SEARCH BAR (Gore)
        search_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.search_input = TextInput(
            hint_text="🔍 Pretraži hranu...",
            multiline=False,
            font_size=18
        )
        self.search_input.bind(text=self.on_search_text)
        search_layout.add_widget(self.search_input)
        
        # 2. REZULTATI PRETRAGE
        self.search_results_layout = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )
        self.search_results_layout.bind(
            minimum_height=self.search_results_layout.setter('height')
        )
        
        search_scroll = ScrollView(size_hint=(1, 0.3))
        search_scroll.add_widget(self.search_results_layout)
        
        # 3. TRENUTNA KALKULACIJA (Sredina)
        calc_label = Label(
            text="📋 Trenutna kalkulacija:",
            size_hint_y=None,
            height=40,
            font_size=18,
            bold=True
        )
        
        self.calculation_layout = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )
        self.calculation_layout.bind(
            minimum_height=self.calculation_layout.setter('height')
        )
        
        calc_scroll = ScrollView(size_hint=(1, 0.4))
        calc_scroll.add_widget(self.calculation_layout)
        
        # 4. UKUPAN ZBIR (Dole)
        self.total_label = Label(
            text="Ukupno: 0.0 UH",
            size_hint_y=None,
            height=60,
            font_size=24,
            bold=True,
            color=(0.2, 0.8, 0.2, 1)
        )
        
        # 5. DUGMAD
        buttons_layout = GridLayout(cols=3, size_hint_y=None, height=60, spacing=10)
        
        btn_add_custom = Button(
            text="➕ Dodaj novi",
            background_color=(0.3, 0.6, 0.9, 1)
        )
        btn_add_custom.bind(on_press=self.show_add_custom_popup)
        
        btn_clear = Button(
            text="🗑 Očisti sve",
            background_color=(0.9, 0.5, 0.2, 1)
        )
        btn_clear.bind(on_press=self.clear_calculation)
        
        btn_save_meal = Button(
            text="💾 Sačuvaj obrok",
            background_color=(0.2, 0.8, 0.4, 1)
        )
        btn_save_meal.bind(on_press=self.show_save_meal_popup)
        
        buttons_layout.add_widget(btn_add_custom)
        buttons_layout.add_widget(btn_clear)
        buttons_layout.add_widget(btn_save_meal)
        
        # Dodaj sve u glavni layout
        main_layout.add_widget(search_layout)
        main_layout.add_widget(search_scroll)
        main_layout.add_widget(calc_label)
        main_layout.add_widget(calc_scroll)
        main_layout.add_widget(self.total_label)
        main_layout.add_widget(buttons_layout)
        
        return main_layout
    
    def on_search_text(self, instance, value):
        """Pretraga u bazi"""
        self.search_results_layout.clear_widgets()
        
        if len(value) < 2:
            return
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT name, gram, unit, carbs_g, category
            FROM items
            WHERE name LIKE ?
            ORDER BY name
            LIMIT 20
        """, (f"%{value}%",))
        
        results = cur.fetchall()
        conn.close()
        
        for row in results:
            item_data = {
                'name': row[0],
                'gram': row[1],
                'unit': row[2],
                'carbs_g': row[3],
                'category': row[4]
            }
            result_item = SearchResultItem(item_data, self.add_to_calculation)
            self.search_results_layout.add_widget(result_item)
    
    def add_to_calculation(self, item_data):
        """Dodaje stavku u kalkulaciju"""
        name = item_data['name']
        uh = item_data['carbs_g']
        
        calc_item = CalculationItem(name, uh, self.remove_from_calculation)
        self.calculation_layout.add_widget(calc_item)
        self.calculation_items.append({'widget': calc_item, 'uh': uh})
        
        self.update_total()
        self.search_input.text = ""  # Očisti search
    
    def remove_from_calculation(self, widget):
        """Uklanja stavku iz kalkulacije"""
        for item in self.calculation_items:
            if item['widget'] == widget:
                self.calculation_items.remove(item)
                self.calculation_layout.remove_widget(widget)
                break
        
        self.update_total()
    
    def update_total(self):
        """Ažurira ukupan zbir UH"""
        self.total_uh = sum(item['uh'] for item in self.calculation_items)
        self.total_label.text = f"Ukupno: {self.total_uh:.1f} UH"
    
    def clear_calculation(self, instance):
        """Briše sve iz kalkulacije"""
        self.calculation_layout.clear_widgets()
        self.calculation_items = []
        self.update_total()
    
    def show_add_custom_popup(self, instance):
        """Popup za ručno dodavanje stavke"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        name_input = TextInput(hint_text="Naziv (npr. Doručak utorkom)", multiline=False)
        uh_input = TextInput(hint_text="UH vrednost (npr. 120)", multiline=False, input_filter='float')
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        popup = Popup(title="Dodaj novu stavku", content=content, size_hint=(0.9, 0.5))
        
        def add_custom():
            if name_input.text and uh_input.text:
                try:
                    uh = float(uh_input.text)
                    item_data = {
                        'name': name_input.text,
                        'carbs_g': uh,
                        'gram': 0,
                        'unit': 'custom',
                        'category': 'custom'
                    }
                    self.add_to_calculation(item_data)
                    popup.dismiss()
                except ValueError:
                    pass
        
        btn_add = Button(text="Dodaj", background_color=(0.2, 0.8, 0.4, 1))
        btn_add.bind(on_press=lambda x: add_custom())
        
        btn_cancel = Button(text="Otkaži", background_color=(0.9, 0.3, 0.3, 1))
        btn_cancel.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(btn_add)
        btn_layout.add_widget(btn_cancel)
        
        content.add_widget(name_input)
        content.add_widget(uh_input)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def show_save_meal_popup(self, instance):
        """Popup za čuvanje obroka"""
        if self.total_uh == 0:
            return
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        name_input = TextInput(hint_text="Naziv obroka (npr. Pileća supa)", multiline=False)
        total_gram_input = TextInput(hint_text="Ukupna količina (g)", multiline=False, input_filter='float')
        unit_gram_input = TextInput(hint_text="Koliko je 1 jedinica (g)", multiline=False, input_filter='float')
        unit_name_input = TextInput(hint_text="Naziv jedinice (npr. porcija, šolja)", multiline=False)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        popup = Popup(title="Sačuvaj kao obrok", content=content, size_hint=(0.9, 0.7))
        
        def save_meal():
            if (name_input.text and total_gram_input.text and 
                unit_gram_input.text and unit_name_input.text):
                try:
                    total_g = float(total_gram_input.text)
                    unit_g = float(unit_gram_input.text)
                    
                    # Računanje UH po jedinici
                    uh_per_unit = self.total_uh * (unit_g / total_g)
                    
                    # Upis u bazu
                    conn = sqlite3.connect(self.db_path)
                    cur = conn.cursor()
                    
                    cur.execute("""
                        INSERT INTO items (name, gram, unit, carbs_g, protein_g, fat_g, category)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (name_input.text, unit_g, unit_name_input.text, uh_per_unit, 0, 0, 'meal'))
                    
                    conn.commit()
                    conn.close()
                    
                    popup.dismiss()
                    self.show_success_popup(f"Obrok '{name_input.text}' sačuvan!\nUH po jedinici: {uh_per_unit:.1f}")
                    
                except ValueError:
                    pass
        
        btn_save = Button(text="Sačuvaj", background_color=(0.2, 0.8, 0.4, 1))
        btn_save.bind(on_press=lambda x: save_meal())
        
        btn_cancel = Button(text="Otkaži", background_color=(0.9, 0.3, 0.3, 1))
        btn_cancel.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(btn_save)
        btn_layout.add_widget(btn_cancel)
        
        content.add_widget(name_input)
        content.add_widget(total_gram_input)
        content.add_widget(unit_gram_input)
        content.add_widget(unit_name_input)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def show_success_popup(self, message):
        """Prikazuje success poruku"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text=message)
        btn = Button(text="OK", size_hint_y=None, height=50)
        
        popup = Popup(title="Uspešno!", content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        
        content.add_widget(label)
        content.add_widget(btn)
        popup.open()


if __name__ == "__main__":
    UHKalkulatorApp().run()

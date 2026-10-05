# Kappen-Inventar — Hello_MOA v1.3

Quelle: `C:\Users\Yogi\OneDrive\Desktop\release_hello_moa_v1.3_2026-09-23.af` (md5-identisch mit
`templates/release/release_hello_moa_v1.3_2026-09-23.af`, Commit `3d2712a`).
Methode: `execute_script` (Affinity SDK) — Face-Nodes aus Layer `底层`, Legenden aus `Alphas_MOA`
+ `images` (Delta-Logo `key_hero_1`/`key_hero_2`), Zuordnung per bbox-Center-Containment
(Marge 15 px). 1U = 225 px @300dpi.

**Kappenzahl gezählt: 133** (134 Kinder in `底层` minus `board_title`, kein Face). Soll laut
Introduction v3.9: 133 → **stimmt exakt überein**, keine Abweichung.

Zonen (gemessene Face-RGB): Cream 232,221,200 · Terracotta 168,93,62 · Taupe 138,120,104 ·
Rosé 200,144,144 · Espresso 26,22,18.
Legenden-Ink (gemessene RGB): Ink(dunkel) 58,42,30 · Gold 212,165,116 · Terracotta-Ink 168,93,62
(AltGr-Glyphen, `_gr`-Suffix).

Spalten: Face-Node | Größe (U, B×H) | Zone | Haupt (Node/Typ/Ink) | Shift-Sub (Node/Ink) |
AltGr (Node/Ink) | Lage.

## Hauptboard

| Face-Node | Größe (U) | Zone | Haupt | Sub | AltGr | Lage |
|---|---|---|---|---|---|---|
| key_hero_1 | 0.96×0.96 | Rosé | delta_hero_1 · EmbeddedDoc (Delta-Logo) | – | – | Board (F-Zeile, rechts außen) |
| key_hero_2 | 0.96×0.96 | Espresso | delta_hero_2 · EmbeddedDoc (Delta-Logo) | – | – | Board (F-Zeile, rechts außen) |
| key_hero_3 | 0.96×0.96 | Rosé | icon_entf_rose · Vektor (Entf-Icon, Ink) | – | – | Board (F-Zeile, rechts außen) |
| key_hero_4 | 0.96×0.96 | Espresso | icon_entf_ink · Vektor (Entf-Icon, Gold) | – | – | Board (F-Zeile, rechts außen) |
| key_f1_face | 0.96×0.96 | Rosé | key_f1 · Vektor "F1", Ink | – | – | Board F-Zeile |
| key_f2_face | 0.96×0.96 | Rosé | key_f2 · Vektor "F2", Ink | – | – | Board F-Zeile |
| key_f3_face | 0.96×0.96 | Rosé | key_f3 · Vektor "F3", Ink | – | – | Board F-Zeile |
| key_f4_face | 0.96×0.96 | Rosé | key_f4 · Vektor "F4", Ink | – | – | Board F-Zeile |
| key_f5_face | 0.96×0.96 | Rosé | key_f5 · Vektor "F5", Ink | – | – | Board F-Zeile |
| key_f6_face | 0.96×0.96 | Rosé | key_f6 · Vektor "F6", Ink | – | – | Board F-Zeile |
| key_f7_face | 0.96×0.96 | Rosé | key_f7 · Vektor "F7", Ink | – | – | Board F-Zeile |
| key_f8_face | 0.96×0.96 | Rosé | key_f8 · Vektor "F8", Ink | – | – | Board F-Zeile |
| key_f9_face | 0.96×0.96 | Rosé | key_f9 · Vektor "F9", Ink | – | – | Board F-Zeile |
| key_f10_face | 0.96×0.96 | Rosé | key_f10 · Vektor "F10", Ink | – | – | Board F-Zeile |
| key_f11_face | 0.96×0.96 | Rosé | key_f11 · Vektor "F11", Ink | – | – | Board F-Zeile |
| key_f12_face | 0.96×0.96 | Rosé | key_f12 · Vektor "F12", Ink | – | – | Board F-Zeile |
| key_esc_face | 0.96×0.96 | Espresso | key_esc · Vektor "ESC", Gold | – | – | Board F-Zeile |
| key_druck_face | 0.96×0.96 | Taupe | icon_druck · Icon (Druck), Ink | – | – | Board F-Zeile |
| key_pause_face | 0.96×0.96 | Taupe | icon_pause · Icon (Pause), Ink | – | – | Board F-Zeile |
| key_rollen_face | 0.96×0.96 | Taupe | icon_rollen · Icon (Rollen), Ink | – | – | Board F-Zeile |
| key_caret_face | 0.96×0.96 | Cream | key_caret "^", Ink | key_caret_sub, Ink | – | Board Zahlenzeile |
| key_num_1_face | 0.96×0.96 | Cream | key_num_1 "1", Ink | key_num_1_sub, Ink | – | Board Zahlenzeile |
| key_num_2_face | 0.96×0.96 | Cream | key_num_2 "2", Ink | key_num_2_sub, Ink | key_num_2_gr, Terracotta | Board Zahlenzeile |
| key_num_3_face | 0.96×0.96 | Cream | key_num_3 "3", Ink | key_num_3_sub, Ink | key_num_3_gr, Terracotta | Board Zahlenzeile |
| key_num_4_face | 0.96×0.96 | Cream | key_num_4 "4", Ink | key_num_4_sub, Ink | – | Board Zahlenzeile |
| key_num_5_face | 0.96×0.96 | Cream | key_num_5 "5", Ink | key_num_5_sub, Ink | – | Board Zahlenzeile |
| key_num_6_face | 0.96×0.96 | Cream | key_num_6 "6", Ink | key_num_6_sub, Ink | – | Board Zahlenzeile |
| key_num_7_face | 0.96×0.96 | Cream | key_num_7 "7", Ink | key_num_7_sub, Ink | key_num_7_gr, Terracotta | Board Zahlenzeile |
| key_num_8_face | 0.96×0.96 | Cream | key_num_8 "8", Ink | key_num_8_sub, Ink | key_num_8_gr, Terracotta | Board Zahlenzeile |
| key_num_9_face | 0.96×0.96 | Cream | key_num_9 "9", Ink | key_num_9_sub, Ink | key_num_9_gr, Terracotta | Board Zahlenzeile |
| key_num_0_face | 0.96×0.96 | Cream | key_num_0 "0", Ink | key_num_0_sub, Ink | key_num_0_gr, Terracotta | Board Zahlenzeile |
| key_ss_face | 0.96×0.96 | Cream | key_ss "ß", Ink | key_ss_sub, Ink | key_ss_gr, Terracotta | Board Zahlenzeile |
| key_acute_face | 0.96×0.96 | Cream | key_acute "´", Ink | key_acute_sub, Ink | – | Board Zahlenzeile |
| key_backspace_face | 1.95×0.96 | Terracotta | key_backspace "⟵", Ink | – | – | Board Zahlenzeile |
| key_bild_up_face | 0.96×0.96 | Taupe | icon_bild_up (Bild↑), Ink | – | – | Board Zahlenzeile |
| key_bild_down_face | 0.96×0.96 | Taupe | icon_bild_down (Bild↓), Ink | – | – | Board Tab-Zeile |
| key_einf_face | 0.96×0.96 | Taupe | icon_einf (Einfügen), Ink | – | – | Board Zahlenzeile |
| key_pos1_face | 0.96×0.96 | Taupe | icon_pos1 (Pos1), Ink | – | – | Board Zahlenzeile |
| key_ende_face | 0.96×0.96 | Taupe | icon_ende (Ende), Ink | – | – | Board Tab-Zeile |
| key_entf_face | 0.96×0.96 | Taupe | icon_entf (Entf), Ink | – | – | Board Tab-Zeile |
| key_numlock_face | 0.96×0.96 | Terracotta | icon_numlock, Ink | – | – | Board Zahlenzeile |
| key_numpad_div_face | 0.96×0.96 | Terracotta | key_numpad_div "/", Ink | – | – | Board Zahlenzeile |
| key_numpad_mul_face | 0.96×0.96 | Terracotta | key_numpad_mul "*", Ink | – | – | Board Zahlenzeile |
| key_numpad_sub_face | 0.96×0.96 | Terracotta | – | key_numpad_sub "-", Ink | – | Board Zahlenzeile |
| key_numpad_plus_face | 0.96×1.95 | Terracotta | key_numpad_plus "+", Ink | – | – | Board (2u vertikal) |
| key_numpad_7_face | 0.96×0.96 | Cream | key_numpad_7 "7", Ink | – | – | Board Tab-Zeile |
| key_numpad_8_face | 0.96×0.96 | Cream | key_numpad_8 "8", Ink | – | – | Board Tab-Zeile |
| key_numpad_9_face | 0.96×0.96 | Cream | key_numpad_9 "9", Ink | – | – | Board Tab-Zeile |
| key_tab_face | 1.46×0.96 | Terracotta | key_tab "↹", Ink | – | – | Board Tab-Zeile |
| key_q_face | 0.96×0.96 | Cream | key_q "Q", Ink | – | key_q_gr, Terracotta | Board Tab-Zeile |
| key_w_face | 0.96×0.96 | Cream | key_w "W", Ink | – | – | Board Tab-Zeile |
| key_e_face | 0.96×0.96 | Cream | key_e "E", Ink | – | key_e_gr, Terracotta | Board Tab-Zeile |
| key_r_face | 0.96×0.96 | Cream | key_r "R", Ink | – | – | Board Tab-Zeile |
| key_t_face | 0.96×0.96 | Cream | key_t "T", Ink | – | – | Board Tab-Zeile |
| key_z_face | 0.96×0.96 | Cream | key_z "Z", Ink | – | – | Board Tab-Zeile |
| key_u_face | 0.96×0.96 | Cream | key_u "U", Ink | – | – | Board Tab-Zeile |
| key_i_face | 0.96×0.96 | Cream | key_i "I", Ink | – | – | Board Tab-Zeile |
| key_o_face | 0.96×0.96 | Cream | key_o "O", Ink | – | – | Board Tab-Zeile |
| key_p_face | 0.96×0.96 | Cream | key_p "P", Ink | – | – | Board Tab-Zeile |
| key_ue_face | 0.96×0.96 | Cream | key_ue "Ü", Ink | – | – | Board Tab-Zeile |
| key_plus_face | 0.96×0.96 | Cream | key_plus "+", Ink | key_plus_sub, Ink | key_plus_gr, Terracotta | Board Tab-Zeile |
| key_hash_ansi | 1.46×0.96 | Cream | key_hash_ansi_legend "#", Ink | key_hash_ansi_sub, Ink | – | Board Tab-Zeile (ANSI-Backslash-Position) |
| key_caps_face | 1.70×0.96 | Terracotta | key_caps "⇪", Ink | – | – | Board CapsLk-Zeile |
| key_a_face | 0.96×0.96 | Cream | key_a "A", Ink | – | – | Board CapsLk-Zeile |
| key_s_face | 0.96×0.96 | Cream | key_s "S", Ink | – | – | Board CapsLk-Zeile |
| key_d_face | 0.96×0.96 | Cream | key_d "D", Ink | – | – | Board CapsLk-Zeile |
| key_f_face | 0.96×0.96 | Cream | key_f "F", Ink | – | – | Board CapsLk-Zeile |
| key_g_face | 0.96×0.96 | Cream | key_g "G", Ink | – | – | Board CapsLk-Zeile |
| key_h_face | 0.96×0.96 | Cream | key_h "H", Ink | – | – | Board CapsLk-Zeile |
| key_j_face | 0.96×0.96 | Cream | key_j "J", Ink | – | – | Board CapsLk-Zeile |
| key_k_face | 0.96×0.96 | Cream | key_k "K", Ink | – | – | Board CapsLk-Zeile |
| key_l_face | 0.96×0.96 | Cream | key_l "L", Ink | – | – | Board CapsLk-Zeile |
| key_oe_face | 0.96×0.96 | Cream | key_oe "Ö", Ink | – | – | Board CapsLk-Zeile |
| key_ae_face | 0.96×0.96 | Cream | key_ae "Ä", Ink | – | – | Board CapsLk-Zeile |
| key_enter_face | 2.21×0.96 | Espresso | key_enter "↵", Gold | – | – | Board CapsLk-Zeile |
| key_numpad_4_face | 0.96×0.96 | Cream | key_numpad_4 "4", Ink | – | – | Board CapsLk-Zeile |
| key_numpad_5_face | 0.96×0.96 | Cream | key_numpad_5 "5", Ink | – | – | Board CapsLk-Zeile |
| key_numpad_6_face | 0.96×0.96 | Cream | key_numpad_6 "6", Ink | – | – | Board CapsLk-Zeile |
| key_shift_l_face | 2.21×0.96 | Terracotta | key_shift_l "⇧", Ink | – | – | Board Shift-Zeile |
| key_shift_r_2.75_face | 2.70×0.96 | Terracotta | key_shift_r "⇧", Ink | – | – | Board Shift-Zeile |
| key_y_face | 0.96×0.96 | Cream | key_y "Y", Ink | – | – | Board Shift-Zeile |
| key_x_face | 0.96×0.96 | Cream | key_x "X", Ink | – | – | Board Shift-Zeile |
| key_c_face | 0.96×0.96 | Cream | key_c "C", Ink | – | – | Board Shift-Zeile |
| key_v_face | 0.96×0.96 | Cream | key_v "V", Ink | – | – | Board Shift-Zeile |
| key_b_face | 0.96×0.96 | Cream | key_b "B", Ink | – | – | Board Shift-Zeile |
| key_n_face | 0.96×0.96 | Cream | key_n "N", Ink | – | – | Board Shift-Zeile |
| key_m_face | 0.96×0.96 | Cream | key_m "M", Ink | – | key_m_gr, Terracotta | Board Shift-Zeile |
| key_semicolon_face | 0.96×0.96 | Cream | key_semicolon ",", Ink | key_semicolon_sub, Ink | – | Board Shift-Zeile |
| key_colon_face | 0.96×0.96 | Cream | key_colon ".", Ink | key_colon_sub, Ink | – | Board Shift-Zeile |
| key_dash_face | 0.96×0.96 | Cream | key_dash "-", Ink | key_dash_sub, Ink | – | Board Shift-Zeile |
| key_arrow_up_face | 0.96×0.96 | Espresso | key_arrow_up "↑", Gold | – | – | Board Shift-Zeile |
| key_numpad_1_face | 0.96×0.96 | Cream | key_numpad_1 "1", Ink | – | – | Board Shift-Zeile |
| key_numpad_2_face | 0.96×0.96 | Cream | key_numpad_2 "2", Ink | – | – | Board Shift-Zeile |
| key_numpad_3_face | 0.96×0.96 | Cream | key_numpad_3 "3", Ink | – | – | Board Shift-Zeile |
| key_numpad_enter_face | 0.96×1.95 | Espresso | key_numpad_enter "↵", Gold | – | – | Board (2u vertikal) |
| key_ctrl_l_face | 1.21×0.96 | Terracotta | key_ctrl_l "STRG", Ink | – | – | Board Bottom-Zeile |
| key_win_face | 1.21×0.96 | Terracotta | key_win "WIN", Ink | – | – | Board Bottom-Zeile |
| key_alt_face | 1.21×0.96 | Terracotta | key_alt "ALT", Ink | – | – | Board Bottom-Zeile |
| key_fn_face | 1.21×0.96 | Terracotta | key_fn "FN", Ink | – | – | Board Bottom-Zeile |
| key_altgr_face | 1.21×0.96 | Terracotta | key_altgr "ALT", Ink | – | – | Board Bottom-Zeile |
| key_ctrl_r_face | 1.21×0.96 | Terracotta | key_ctrl_r "STRG", Ink | – | – | Board Bottom-Zeile |
| key_menu_face | 1.21×0.96 | Terracotta | key_menu (Menü-Icon), Ink | – | – | Board Bottom-Zeile |
| key_space_face | 6.19×0.96 | Espresso | key_space + key_space_eq (Delta-Logo/Equalizer), Gold | – | – | Board Bottom-Zeile (Leertaste) |
| key_numpad_0_face | 1.95×0.96 | Cream | key_numpad_0 "0", Ink | – | – | Board Bottom-Zeile |
| key_numpad_dot_face | 0.96×0.96 | Cream | key_numpad_dot ".", Ink (seit 2026-10-05 in Hello_MOA_v1.33.af, vorher icon_numpad_entf; oben, horizontal zentriert wie Numpad-Ziffern; Face am 2026-10-05 von key_numpad_entf_face umbenannt) | – | – | Board Bottom-Zeile |
| key_arrow_down_face | 0.96×0.96 | Espresso | key_arrow_down "↓", Gold | – | – | Board Bottom-Zeile |
| key_arrow_left_face | 0.96×0.96 | Espresso | key_arrow_left "←", Gold | – | – | Board Bottom-Zeile |
| key_arrow_right_face | 0.96×0.96 | Espresso | key_arrow_right "→", Gold | – | – | Board Bottom-Zeile |
| key_enter_iso_face | **ISO-Enter** 1.55×2.07 | Espresso | key_enter_iso "↵", Gold | – | – | Board (ISO-Block) |

## Zusatz-/Alternativkappen (außerhalb des Hauptboards, y≥2700px)

| Face-Node | Größe (U) | Zone | Haupt | Sub | AltGr | Hinweis |
|---|---|---|---|---|---|---|
| novelty_note_face (key_note_face) | 0.96×0.96 | Taupe | novelty_note (Notensymbol), Ink | – | – | Novelty-Spare |
| novelty_vinyl_face (key_disk_face) | 0.96×0.96 | Taupe | novelty_vinyl (Schallplatte), Ink | – | – | Novelty-Spare |
| novelty_eq_face (key_eq_face) | 0.96×0.96 | Taupe | novelty_eq (Equalizer), Ink | – | – | Novelty-Spare |
| novelty_dial_face (key_dial_face) | 0.96×0.96 | Taupe | novelty_dial (Wählscheibe), Ink | – | – | Novelty-Spare |
| novelty_mic_face (key_mic_face) | 0.96×0.96 | Taupe | novelty_mic (Mikrofon), Ink | – | – | Novelty-Spare |
| key_note_2_face (novelty_note2) | 0.96×0.96 | Taupe | novelty_note2 (Noten-Variante), Ink | – | – | Novelty-Spare |
| key_cassette_face | 0.96×0.96 | Rosé | novelty_cassette (Kassette), Ink | – | – | Novelty-Spare |
| key_numpad_0_1u_face | 0.96×0.96 | Cream | key_numpad_0_1u "0", Ink | – | – | Novelty-Spare (Platz der früheren key_head_set_face; seit 2026-10-05 in Hello_MOA_v1.33.af, key_head_set_face + novelty_headphones entfernt) |
| key_heart_face | 0.96×0.96 | Rosé | novelty_heart (Herz), Ink | – | – | Novelty-Spare |
| key_vol_up_face | 0.96×0.96 | Rosé | novelty_vol_up (Lautstärke+), Ink | – | – | Novelty-Spare |
| key_vol_down_face | 0.96×0.96 | Rosé | novelty_vol_down (Lautstärke-), Ink | – | – | Novelty-Spare |
| key_fn_1u_face | 0.96×0.96 | Terracotta | key_fn_1u "FN", Ink | – | – | 1u-Größenvariante |
| key_menu_1u_face | 0.96×0.96 | Terracotta | key_menu_1u (Menü-Icon), Ink | – | – | 1u-Größenvariante |
| key_alt_1u_face | 0.96×0.96 | Terracotta | key_alt_1u "ALT", Ink | – | – | 1u-Größenvariante |
| key_ctrl_1u_face | 0.96×0.96 | Terracotta | key_ctrl_1u "STRG", Ink | – | – | 1u-Größenvariante |
| key_shift_1.75u_face | 1.70×0.96 | Terracotta | key_shift_1.75u "⇧", Ink | – | – | Shift-Größenvariante |
| key_shift_1.25u_face | 1.21×0.96 | Terracotta | key_shift_1.25u "⇧", Ink | – | – | Shift-Größenvariante |
| key_shift_2u_face | 1.95×0.96 | Terracotta | key_shift_2u "⇧", Ink | – | – | Shift-Größenvariante |
| key_shift_1u_face_new | 0.96×0.96 | Terracotta | key_shift_1u_new "⇧", Ink | – | – | Shift-Größenvariante |
| key_hash_face | 0.96×0.96 | Cream | key_hash "#", Ink | key_hash_sub, Ink | – | Alt-Positions-Kappe (ISO #-Taste) |
| key_less_face | 0.96×0.96 | Cream | key_less "<", Ink | key_less_sub, Ink | key_less_gr, Terracotta | Alt-Positions-Kappe (ISO <>) |
| key_druck_rose_face | 0.96×0.96 | Rosé | icon_druck_rose (Druck), Ink | – | – | Farbvariante Rosé |
| key_rollen_rose_face | 0.96×0.96 | Rosé | icon_rollen_rose (Rollen), Ink | – | – | Farbvariante Rosé |
| key_pause_rose_face | 0.96×0.96 | Rosé | icon_pause_rose (Pause), Ink | – | – | Farbvariante Rosé |

## Kappen ohne Legende
Keine. `key_hero_1`/`key_hero_2` sahen zunächst legendenlos aus (nicht in `Alphas_MOA`) — ihre
Legende liegt als `EmbeddedDocumentNode` (`delta_hero_1`/`delta_hero_2`, Delta-Logo) im Layer
`images`, nicht in `Alphas_MOA`. Mit dieser Erweiterung sind alle 133 Faces zugeordnet.

## Nicht eindeutig zuordenbar
Keine Restfälle nach bbox-Center-Matching (Marge 15 px); 0 unmatched Legenden, 0 Faces ohne
Legende (nach Einbezug von `images`).

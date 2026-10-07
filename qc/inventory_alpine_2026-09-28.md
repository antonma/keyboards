# Kappen-Inventar — DELTASET-Alpine-133 (Release)

> Abgelöst durch inventory_alpine_2026-10-04.md (neue Node-Namen, Spalte Reihe)

Quelle: `D:\repos\GitHub\keyboards\templates\release\release_alpine_133_2026-09-23.af`, Commit
`6afa068`. Methode: `execute_script` (Affinity SDK) — Face-Nodes aus Layer `底色`, Legenden aus
`Alphas_Alpine` + `Images` (Delta-Logo `key_empty_icon`), Zuordnung per bbox-Center-Containment
(Marge 15 px). 1U = 225 px @300dpi.

**Kappenzahl gezählt: 131** (132 Kinder in `底色` minus `template_annotation`, kein Face). Soll
laut Introduction v3.9: 131 → **stimmt exakt überein**. (Layer `键帽` enthält zusätzlich 4
Board-weite Artwork-Overlays `keycap_art_1..4`, das sind keine Einzelkappen und wurden nicht
mitgezählt.)

Zonen (gemessene Face-RGB): Snow 244,241,235 · Onyx 30,30,34 · Brake-red 200,16,46 ·
Ash-Rosé 176,118,128.
Legendentypen: **Vektor-Glyph** (PolyCurveNode, Alpha/Numerik/Sonderzeichen — Ink 26,26,30,
AltGr `_gr` in Brake-red 200,16,46) · **Dot-Matrix** (ContainerNode aus Einzelpunkten — bei
F-Zeile/Modifiern durchgehend dunkel ~16,19,22; bei `key_druck_pixels` Farbverlauf
dunkelrot→hellrosa ~22,20,26 bis 255,110,130, stichprobenhaft an 1 Icon gemessen, n=1) ·
**EmbeddedDoc** (`key_empty_icon`, Delta-Logo).

## Hauptboard

| Face-Node | Größe (U) | Zone | Haupt (Typ, Ink) | Sub | AltGr | Lage |
|---|---|---|---|---|---|---|
| key_esc_face | 0.95×0.95 | Brake-red | key_esc_pixels · Dot-Matrix "ESC" | – | – | F-Zeile |
| key_f1_face | 0.95×0.95 | Onyx | key_f1_pixels · Dot-Matrix "F1" | – | – | F-Zeile |
| key_f2_face | 0.95×0.95 | Onyx | key_f2_pixels · Dot-Matrix "F2" | – | – | F-Zeile |
| key_f3_face | 0.95×0.95 | Onyx | key_f3_pixels · Dot-Matrix "F3" | – | – | F-Zeile |
| key_f4_face | 0.95×0.95 | Onyx | key_f4_pixels · Dot-Matrix "F4" | – | – | F-Zeile |
| key_f5_face | 0.95×0.95 | Onyx | key_f5_pixels · Dot-Matrix "F5" | – | – | F-Zeile |
| key_f6_face | 0.95×0.95 | Onyx | key_f6_pixels · Dot-Matrix "F6" | – | – | F-Zeile |
| key_f7_face | 0.95×0.95 | Onyx | key_f7_pixels · Dot-Matrix "F7" | – | – | F-Zeile |
| key_f8_face | 0.95×0.95 | Onyx | key_f8_pixels · Dot-Matrix "F8" | – | – | F-Zeile |
| key_f9_face | 0.95×0.95 | Onyx | key_f9_pixels · Dot-Matrix "F9" | – | – | F-Zeile |
| key_f10_face | 0.95×0.95 | Onyx | key_f10_pixels · Dot-Matrix "F10" | – | – | F-Zeile |
| key_f11_face | 0.95×0.95 | Onyx | key_f11_pixels · Dot-Matrix "F11" | – | – | F-Zeile |
| key_f12_face | 0.95×0.95 | Onyx | key_f12_pixels · Dot-Matrix "F12" | – | – | F-Zeile |
| key_druck_face | 0.95×0.95 | Snow | key_druck_pixels · Dot-Matrix (Druck-Icon) | – | – | F-Zeile |
| key_rollen_face | 0.95×0.95 | Snow | key_rollen_pixels · Dot-Matrix (Rollen-Icon) | – | – | F-Zeile |
| key_pause_face | 0.95×0.95 | Snow | key_pause_pixels · Dot-Matrix (Pause-Icon) | – | – | F-Zeile |
| key_einf_r1_face | 0.95×0.95 | Onyx | key_einf_r1_pixels · Dot-Matrix (Einfügen) | – | – | F-Zeile (Alt-Position) |
| key_empty_face | 0.95×0.95 | Brake-red | key_empty_icon · EmbeddedDoc (Delta-Logo) | – | – | F-Zeile, ganz rechts |
| key_entf_r1_face | 0.95×0.95 | Onyx | key_entf_r1_pixels · Dot-Matrix (Entf) | – | – | F-Zeile (Alt-Position) |
| key_exit_r1_face | 0.95×0.95 | Onyx | key_exit_r1_pixels · Dot-Matrix (Exit/Power-Icon) | – | – | F-Zeile (Alt-Position) |
| key_caret_face | 0.95×0.95 | Snow | key_caret "^" Vektor, Ink | key_caret_sub, Ink | – | Zahlenzeile |
| key_num_1_face | 0.95×0.95 | Snow | key_num_1 "1" Vektor, Ink | key_num_1_sub, Ink | – | Zahlenzeile |
| key_num_2_face | 0.95×0.95 | Snow | key_num_2 "2" Vektor, Ink | key_num_2_sub, Ink | key_num_2_gr, Brake-red | Zahlenzeile |
| key_num_3_face | 0.95×0.95 | Snow | key_num_3 "3" Vektor, Ink | key_num_3_sub, Ink | key_num_3_gr, Brake-red | Zahlenzeile |
| key_num_4_face | 0.95×0.95 | Snow | key_num_4 "4" Vektor, Ink | key_num_4_sub, Ink | – | Zahlenzeile |
| key_num_5_face | 0.95×0.95 | Snow | key_num_5 "5" Vektor, Ink | key_num_5_sub, Ink | – | Zahlenzeile |
| key_num_6_face | 0.95×0.95 | Snow | key_num_6 "6" Vektor, Ink | key_num_6_sub, Ink | – | Zahlenzeile |
| key_num_7_face | 0.95×0.95 | Snow | key_num_7 "7" Vektor, Ink | key_num_7_sub, Ink | key_num_7_gr, Brake-red | Zahlenzeile |
| key_num_8_face | 0.95×0.95 | Snow | key_num_8 "8" Vektor, Ink | key_num_8_sub, Ink | key_num_8_gr, Brake-red | Zahlenzeile |
| key_num_9_face | 0.95×0.95 | Snow | key_num_9 "9" Vektor, Ink | key_num_9_sub, Ink | key_num_9_gr, Brake-red | Zahlenzeile |
| key_num_0_face | 0.95×0.95 | Snow | key_num_0 "0" Vektor, Ink | key_num_0_sub, Ink | key_num_0_gr, Brake-red | Zahlenzeile |
| key_ss_face | 0.95×0.95 | Snow | key_ss "ß" Vektor, Ink | key_ss_sub, Ink | key_ss_gr, Brake-red | Zahlenzeile |
| key_acute_face | 0.95×0.95 | Snow | key_acute "´" Vektor, Ink | key_acute_sub, Ink | – | Zahlenzeile |
| key_backspace_face | 1.96×0.95 | Onyx | key_backspace_pixels · Dot-Matrix "⟵" | – | – | Zahlenzeile |
| key_einf_face | 0.95×0.95 | Snow | key_einf_pixels · Dot-Matrix (Einfügen) | – | – | Zahlenzeile |
| key_pos1_face | 0.95×0.95 | Snow | key_pos1_pixels · Dot-Matrix (Pos1) | – | – | Zahlenzeile |
| key_bild_up_face | 0.95×0.95 | Snow | key_bild_up_pixels · Dot-Matrix (Bild↑) | – | – | Zahlenzeile |
| key_numlock_face | 0.95×0.95 | Onyx | key_numlock_pixels · Dot-Matrix (Numlock) | – | – | Zahlenzeile |
| key_numpad_div_r1_face | 0.95×0.95 | Onyx | key_numpad_div_r1 "/" Vektor (Snow-Ink) | – | – | Zahlenzeile |
| key_numpad_mul_r1_face | 0.95×0.95 | Onyx | key_numpad_mul_r1 "*" Vektor (Snow-Ink) | – | – | Zahlenzeile |
| key_numpad_sub_r1_face | 0.95×0.95 | Onyx | key_numpad_sub_r1 "-" Vektor (Snow-Ink) | – | – | Zahlenzeile |
| key_hash_r4_face | 1.46×0.95 | Ash-Rosé | key_hash_r4 "#" Vektor, Ink | key_hash_r4_sub, Ink | – | Tab-Zeile (Alt-Position) |
| key_numpad_plus_face | 0.95×1.95 | Onyx | key_numpad_plus "+" Vektor (Snow-Ink) | – | – | Zahlenzeile (2u vertikal) |
| key_tab_face | 1.46×0.95 | Onyx | key_tab_pixels · Dot-Matrix "↹" | – | – | Tab-Zeile |
| key_q_face | 0.95×0.95 | Snow | key_q "Q" Vektor, Ink | – | key_q_gr, Brake-red | Tab-Zeile |
| key_w_face | 0.95×0.95 | Snow | key_w "W" Vektor, Ink | – | – | Tab-Zeile |
| key_e_face | 0.95×0.95 | Snow | key_e "E" Vektor, Ink | – | key_e_gr, Brake-red | Tab-Zeile |
| key_r_face | 0.95×0.95 | Snow | key_r "R" Vektor, Ink | – | – | Tab-Zeile |
| key_t_face | 0.95×0.95 | Snow | key_t "T" Vektor, Ink | – | – | Tab-Zeile |
| key_z_face | 0.95×0.95 | Snow | key_z "Z" Vektor, Ink | – | – | Tab-Zeile |
| key_u_face | 0.95×0.95 | Snow | key_u "U" Vektor, Ink | – | – | Tab-Zeile |
| key_i_face | 0.95×0.95 | Snow | key_i "I" Vektor, Ink | – | – | Tab-Zeile |
| key_o_face | 0.95×0.95 | Snow | key_o "O" Vektor, Ink | – | – | Tab-Zeile |
| key_p_face | 0.95×0.95 | Snow | key_p "P" Vektor, Ink | – | – | Tab-Zeile |
| key_ue_face | 0.95×0.95 | Snow | key_ue "Ü" Vektor, Ink | – | – | Tab-Zeile |
| key_plus_face | 0.95×0.95 | Snow | key_plus "+" Vektor, Ink | key_plus_sub, Ink | key_plus_gr, Brake-red | Tab-Zeile |
| key_entf_face | 0.95×0.95 | Snow | key_entf_pixels · Dot-Matrix (Entf) | – | – | Tab-Zeile |
| key_ende_face | 0.95×0.95 | Snow | key_ende_pixels · Dot-Matrix (Ende) | – | – | Tab-Zeile |
| key_bild_down_face | 0.95×0.95 | Snow | key_bild_down_pixels · Dot-Matrix (Bild↓) | – | – | Tab-Zeile |
| key_numpad_7_face | 0.95×0.95 | Snow | key_numpad_7 "7" Vektor, Ink | – | – | Tab-Zeile |
| key_numpad_8_face | 0.95×0.95 | Snow | key_numpad_8 "8" Vektor, Ink | – | – | Tab-Zeile |
| key_numpad_9_face | 0.95×0.95 | Snow | key_numpad_9 "9" Vektor, Ink | – | – | Tab-Zeile |
| key_caps_face | 1.71×0.95 | Onyx | key_caps_pixels · Dot-Matrix "⇪" | – | – | CapsLk-Zeile |
| key_a_face | 0.95×0.95 | Snow | key_a "A" Vektor, Ink | – | – | CapsLk-Zeile |
| key_s_face | 0.95×0.95 | Snow | key_s "S" Vektor, Ink | – | – | CapsLk-Zeile |
| key_d_face | 0.95×0.95 | Snow | key_d "D" Vektor, Ink | – | – | CapsLk-Zeile |
| key_f_face | 0.95×0.95 | Snow | key_f "F" Vektor, Ink | – | – | CapsLk-Zeile |
| key_g_face | 0.95×0.95 | Snow | key_g "G" Vektor, Ink | – | – | CapsLk-Zeile |
| key_h_face | 0.95×0.95 | Snow | key_h "H" Vektor, Ink | – | – | CapsLk-Zeile |
| key_j_face | 0.95×0.95 | Snow | key_j "J" Vektor, Ink | – | – | CapsLk-Zeile |
| key_k_face | 0.95×0.95 | Snow | key_k "K" Vektor, Ink | – | – | CapsLk-Zeile |
| key_l_face | 0.95×0.95 | Snow | key_l "L" Vektor, Ink | – | – | CapsLk-Zeile |
| key_oe_face | 0.95×0.95 | Snow | key_oe "Ö" Vektor, Ink | – | – | CapsLk-Zeile |
| key_ae_face | 0.95×0.95 | Snow | key_ae "Ä" Vektor, Ink | – | – | CapsLk-Zeile |
| key_enter_face | 2.21×0.95 | Brake-red | key_enter_pixels · Dot-Matrix "↵" | – | – | CapsLk-Zeile |
| key_numpad_4_face | 0.95×0.95 | Snow | key_numpad_4 "4" Vektor, Ink | – | – | CapsLk-Zeile |
| key_numpad_5_face | 0.95×0.95 | Snow | key_numpad_5 "5" Vektor, Ink | – | – | CapsLk-Zeile |
| key_numpad_6_face | 0.95×0.95 | Snow | key_numpad_6 "6" Vektor, Ink | – | – | CapsLk-Zeile |
| key_shift_r_face | 2.68×0.95 | Onyx | key_shift_r_pixels · Dot-Matrix "⇧" | – | – | Shift-Zeile |
| key_arrow_up_face | 0.95×0.95 | Snow | key_arrow_up_pixels · Dot-Matrix "↑" | – | – | Shift-Zeile |
| key_numpad_1_face | 0.95×0.95 | Snow | key_numpad_1 "1" Vektor, Ink | – | – | Shift-Zeile |
| key_numpad_2_face | 0.95×0.95 | Snow | key_numpad_2 "2" Vektor, Ink | – | – | Shift-Zeile |
| key_numpad_3_face | 0.95×0.95 | Snow | key_numpad_3 "3" Vektor, Ink | – | – | Shift-Zeile |
| key_shift_l_face | 2.21×0.95 | Onyx | key_shift_l_pixels · Dot-Matrix "⇧" | – | – | Shift-Zeile |
| key_numpad_enter_face | 0.95×1.95 | Brake-red | key_numpad_enter_pixels · Dot-Matrix "↵" | – | – | Shift-Zeile (2u vertikal) |
| key_y_face | 0.95×0.95 | Snow | key_y "Y" Vektor, Ink | – | – | Shift-Zeile |
| key_x_face | 0.95×0.95 | Snow | key_x "X" Vektor, Ink | – | – | Shift-Zeile |
| key_c_face | 0.95×0.95 | Snow | key_c "C" Vektor, Ink | – | – | Shift-Zeile |
| key_v_face | 0.95×0.95 | Snow | key_v "V" Vektor, Ink | – | – | Shift-Zeile |
| key_b_face | 0.95×0.95 | Snow | key_b "B" Vektor, Ink | – | – | Shift-Zeile |
| key_n_face | 0.95×0.95 | Snow | key_n "N" Vektor, Ink | – | – | Shift-Zeile |
| key_m_face | 0.95×0.95 | Snow | key_m "M" Vektor, Ink | – | key_m_gr, Brake-red | Shift-Zeile |
| key_semicolon_face | 0.95×0.95 | Snow | key_semicolon "," Vektor, Ink | key_semicolon_sub, Ink | – | Shift-Zeile |
| key_colon_face | 0.95×0.95 | Snow | key_colon "." Vektor, Ink | key_colon_sub, Ink | – | Shift-Zeile |
| key_dash_face | 0.95×0.95 | Snow | key_dash "-" Vektor, Ink | key_dash_sub, Ink | – | Shift-Zeile |
| key_arrow_left_face | 0.95×0.95 | Snow | key_arrow_left_pixels · Dot-Matrix "←" | – | – | Bottom-Zeile |
| key_arrow_down_face | 0.95×0.95 | Snow | key_arrow_down_pixels · Dot-Matrix "↓" | – | – | Bottom-Zeile |
| key_arrow_right_face | 0.95×0.95 | Snow | key_arrow_right_pixels · Dot-Matrix "→" | – | – | Bottom-Zeile |
| key_numpad_0_face | 1.96×0.95 | Snow | key_numpad_0 "0" Vektor, Ink | – | – | Bottom-Zeile |
| key_numpad_entf_r1_face | 0.95×0.95 | Snow | key_numpad_entf_r1_pixels · Dot-Matrix (Entf) | – | – | Bottom-Zeile |
| key_ctrl_l_face | 1.18×0.95 | Onyx | key_ctrl_l_pixels · Dot-Matrix "STRG" | – | – | Bottom-Zeile |
| key_win_face | 1.18×0.95 | Onyx | key_win_pixels · Dot-Matrix "WIN" | – | – | Bottom-Zeile |
| key_alt_face | 1.18×0.95 | Onyx | key_alt_pixels · Dot-Matrix "ALT" | – | – | Bottom-Zeile |
| key_space_face | 6.20×0.95 | Snow | key_space_pixels · Dot-Matrix (Delta-Logo/EQ) | – | – | Bottom-Zeile (Leertaste) |
| key_altgr_face | 1.18×0.95 | Onyx | key_altgr_pixels · Dot-Matrix "ALT" | – | – | Bottom-Zeile |
| key_fn_r_face | 1.18×0.95 | Onyx | key_fn_r_pixels · Dot-Matrix "Fn" | – | – | Bottom-Zeile — *geändert 2026-10-01 (Alpine-134): vorher key_win_r_face / key_win_r_pixels "WIN"* |
| key_menu_face | 1.18×0.95 | Ash-Rosé | key_menu_pixels · Dot-Matrix (Menü-Icon) | – | – | Bottom-Zeile |
| key_ctrl_r_face | 1.18×0.95 | Onyx | key_ctrl_r_pixels · Dot-Matrix "STRG" | – | – | Bottom-Zeile |
| key_ISO_Enter_r3_face | **ISO-Enter** 1.48×1.97 | Brake-red | key_ISO_Enter_r3_pixels · Dot-Matrix "↵" | – | – | ISO-Block |

## Zusatz-/Alternativkappen (außerhalb des Hauptboards)

| Face-Node | Größe (U) | Zone | Haupt (Typ, Ink) | Sub | AltGr | Hinweis |
|---|---|---|---|---|---|---|
| key_fancy_1_r6_face | 0.95×0.95 | Onyx | key_fancy_1_r6_pixels · Dot-Matrix (Fancy-Icon 1) | – | – | Novelty-Spare |
| key_fancy_2_r6_face | 0.95×0.95 | Onyx | key_fancy_2_r6_pixels · Dot-Matrix (Fancy-Icon 2) | – | – | Novelty-Spare |
| key_fancy_3_r6_face | 0.95×0.95 | Onyx | key_fancy_3_r6_pixels · Dot-Matrix (Fancy-Icon 3) | – | – | Novelty-Spare |
| key_bild_up_r4_face | 0.95×0.95 | Snow | key_bild_up_r4_pixels · Dot-Matrix (Bild↑) | – | – | Alt-Positions-Kappe |
| key_hash_r3_face | 0.95×0.95 | Snow | key_hash_r3 "#" Vektor, Ink | key_hash_r3_sub, Ink | – | Alt-Positions-Kappe |
| key_bild_down_r3_face | 0.95×0.95 | Snow | key_bild_down_r3_pixels · Dot-Matrix (Bild↓) | – | – | Alt-Positions-Kappe |
| key_entf_r3_face | 0.95×0.95 | Snow | key_entf_r3_pixels · Dot-Matrix (Entf) | – | – | Alt-Positions-Kappe |
| key_bild_up_r3_face | 0.95×0.95 | Snow | key_bild_up_r3_pixels · Dot-Matrix (Bild↑) | – | – | Alt-Positions-Kappe |
| key_ende_r3_face | 0.95×0.95 | Snow | key_ende_r3_pixels · Dot-Matrix (Ende) | – | – | Alt-Positions-Kappe |
| key_bild_down_r2_face | 0.95×0.95 | Snow | key_bild_down_r2_pixels · Dot-Matrix (Bild↓) | – | – | Alt-Positions-Kappe |
| key_ende_r2_face | 0.95×0.95 | Snow | key_ende_r2_pixels · Dot-Matrix (Ende) | – | – | Alt-Positions-Kappe |
| key_entf_r2_face | 0.95×0.95 | Snow | key_entf_r2_pixels · Dot-Matrix (Entf) | – | – | Alt-Positions-Kappe |
| key_1u_shift_r2_face | 0.95×0.95 | Onyx | key_1u_shift_r2_pixels · Dot-Matrix "⇧" | – | – | Shift-Größenvariante |
| key_less_r2_face | 0.95×0.95 | Snow | key_less_r2 "<" Vektor, Ink | key_less_r2_sub, Ink | key_less_r2_gr, Brake-red | Alt-Positions-Kappe |
| key_1.25u_shift_r2_face | 1.18×0.95 | Ash-Rosé | key_1.25u_shift_r2_pixels · Dot-Matrix "⇧" | – | – | Shift-Größenvariante |
| key_1.75u_shift_r2_face | 1.71×0.95 | Onyx | key_1.75u_shift_r2_pixels · Dot-Matrix "⇧" | – | – | Shift-Größenvariante |
| key_2u_shift_r2_face | 1.96×0.95 | Onyx | key_2u_shift_r2_pixels · Dot-Matrix "⇧" | – | – | Shift-Größenvariante |
| key_numpad_0_r1_face | 0.95×0.95 | Snow | key_numpad_0_r1 "0" Vektor, Ink | – | – | Alt-Positions-Kappe |
| key_strg_r1_face | 0.95×0.95 | Onyx | key_strg_r1_pixels · Dot-Matrix "STRG" | – | – | Alt-Positions-Kappe |
| key_menu_r1_face | 0.95×0.95 | Onyx | key_menu_r1_pixels · Dot-Matrix (Menü-Icon) | – | – | Alt-Positions-Kappe |
| key_alt_r1_face | 0.95×0.95 | Onyx | key_alt_r1_pixels · Dot-Matrix "ALT" | – | – | Alt-Positions-Kappe |
| key_fn_r1_face | 0.95×0.95 | Ash-Rosé | key_fn_r1_pixels · Dot-Matrix "FN" | – | – | Alt-Positions-Kappe |

## Kappen ohne Legende
Keine. Alle 131 Faces haben eine Legende (bbox-Center-Matching, Marge 15 px), inkl.
`key_empty_face` → `key_empty_icon` (EmbeddedDoc, Layer `Images`).

## Nicht eindeutig zuordenbar
0 unmatched Legenden, 0 Faces ohne Legende. Einzige Unsicherheit: die genaue Ink-Farbwertspanne
der Dot-Matrix-Icons wurde nur an 2 Beispiel-Icons (`key_esc_pixels`, `key_druck_pixels`)
stichprobenhaft gemessen (n=2 von ~60 Dot-Matrix-Legenden) — für alle anderen Dot-Matrix-Legenden
wurde die Ink-Farbe NICHT einzeln gemessen (nur Typ "Dot-Matrix" over bbox-Match bestätigt).

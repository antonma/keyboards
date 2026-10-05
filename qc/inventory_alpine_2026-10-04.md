# Kappen-Inventar — DELTASET-Alpine-134 (Node-Namen mit Reihe, Stand 2026-10-04)

Abgelöst-Hinweis: ersetzt `inventory_alpine_2026-09-28.md` (alte Node-Namen, ohne Reihe).

Quelle: Arbeitsdatei `templates/hersteller/Alpine/DELTASET-Alpine-134.af` nach der `_rN`-Umbenennung
vom 2026-10-04 (590 Nodes, Selbstcheck ok); Namen aus `qc/alpine_row_mapping_2026-10-04_final.json`
(`faces`, `rename_face_und_legenden`). Größe, Zone, Legendeninhalt und Legendentyp sind aus
`qc/inventory_alpine_2026-09-28.md` übernommen (dort per Affinity-SDK gemessen; Win R → Fn R aus Alpine-134);
sie wurden hier nicht neu gemessen. Legenden-Node-Namen sind auf die neuen Namen umgestellt.

**Kappenzahl: 131** (Hauptboard 108, Zusatzkappen 23).

Reihen-Konvention (STA-Reihe im Namen `key_<name>_r<N>`): R6 = F-Reihe, R5 = Zahlenreihe,
R4 = Tab-Reihe, R3 = Caps-Reihe, R2 = Shift-Reihe, R1 = Strg-Reihe. Kappen über zwei Reihen heißen
`_r4_r3` bzw. `_r2_r1` (obere Reihe zuerst) und zählen unten zur **unteren** Reihe (Feld `row` im Mapping).
1U-Zusatzkappen tragen `_1u` vor der Reihe (`key_alt_1u_r1`, `key_menu_1u_r1`, `key_numpad_0_1u_r1`).
Rechte Strg heißt `key_ctrl_r_r1`, rechtes Fn `key_fn_r_r1` (Seite + Reihe).

**Zählung je Reihe:** R6 23 · R5 21 · R4 21 · R3 23 · R2 24 · R1 19 = 131

Zonen: Snow 244,241,235 · Onyx 30,30,34 · Brake-red 200,16,46 · Ash-Rosé 176,118,128.
Legendentypen: Vektor-Glyph (Alpha/Numerik/Sonderzeichen, Ink 30,30,34 seit 2026-10-05, vorher 26,26,30 — Anton: ein Dunkelton für alle einfarbigen dunklen Tinten inkl. Enter-/Esc-Zeichen und Ash-Badges; AltGr `_gr` Brake-red) ·
Dot-Matrix (`_pixels`, ContainerNode aus Einzelpunkten) · EmbeddedDoc (`key_empty_r6_icon`, Delta-Logo).
Die Spalte „Lage“ des alten Inventars entfällt, die Reihe ersetzt sie. Ink-Farben der Dot-Matrix-Icons
wurden nur stichprobenhaft gemessen (n=2, siehe altes Inventar).

## Kappen je Reihe (Hauptboard zuerst, dann Zusatzkappen)

### R6 (23 Kappen: 20 Hauptboard, 3 Zusatz)

| Reihe | Face-Node (neu) | alter Name | Größe (U) | Zone | Haupt | Sub | AltGr | Block |
|---|---|---|---|---|---|---|---|---|
| R6 | key_esc_r6_face | key_esc_face | 0.95×0.95 | Brake-red | key_esc_r6_pixels · Dot-Matrix "ESC" | – | – | Hauptboard |
| R6 | key_f1_r6_face | key_f1_face | 0.95×0.95 | Onyx | key_f1_r6_pixels · Dot-Matrix "F1" | – | – | Hauptboard |
| R6 | key_f2_r6_face | key_f2_face | 0.95×0.95 | Onyx | key_f2_r6_pixels · Dot-Matrix "F2" | – | – | Hauptboard |
| R6 | key_f3_r6_face | key_f3_face | 0.95×0.95 | Onyx | key_f3_r6_pixels · Dot-Matrix "F3" | – | – | Hauptboard |
| R6 | key_f4_r6_face | key_f4_face | 0.95×0.95 | Onyx | key_f4_r6_pixels · Dot-Matrix "F4" | – | – | Hauptboard |
| R6 | key_f5_r6_face | key_f5_face | 0.95×0.95 | Onyx | key_f5_r6_pixels · Dot-Matrix "F5" | – | – | Hauptboard |
| R6 | key_f6_r6_face | key_f6_face | 0.95×0.95 | Onyx | key_f6_r6_pixels · Dot-Matrix "F6" | – | – | Hauptboard |
| R6 | key_f7_r6_face | key_f7_face | 0.95×0.95 | Onyx | key_f7_r6_pixels · Dot-Matrix "F7" | – | – | Hauptboard |
| R6 | key_f8_r6_face | key_f8_face | 0.95×0.95 | Onyx | key_f8_r6_pixels · Dot-Matrix "F8" | – | – | Hauptboard |
| R6 | key_f9_r6_face | key_f9_face | 0.95×0.95 | Onyx | key_f9_r6_pixels · Dot-Matrix "F9" | – | – | Hauptboard |
| R6 | key_f10_r6_face | key_f10_face | 0.95×0.95 | Onyx | key_f10_r6_pixels · Dot-Matrix "F10" | – | – | Hauptboard |
| R6 | key_f11_r6_face | key_f11_face | 0.95×0.95 | Onyx | key_f11_r6_pixels · Dot-Matrix "F11" | – | – | Hauptboard |
| R6 | key_f12_r6_face | key_f12_face | 0.95×0.95 | Onyx | key_f12_r6_pixels · Dot-Matrix "F12" | – | – | Hauptboard |
| R6 | key_druck_r6_face | key_druck_face | 0.95×0.95 | Snow | key_druck_r6_pixels · Dot-Matrix (Druck-Icon) | – | – | Hauptboard |
| R6 | key_rollen_r6_face | key_rollen_face | 0.95×0.95 | Snow | key_rollen_r6_pixels · Dot-Matrix (Rollen-Icon) | – | – | Hauptboard |
| R6 | key_pause_r6_face | key_pause_face | 0.95×0.95 | Snow | key_pause_r6_pixels · Dot-Matrix (Pause-Icon) | – | – | Hauptboard |
| R6 | key_einf_r6_face | key_einf_r1_face | 0.95×0.95 | Onyx | key_einf_r6_pixels · Dot-Matrix (Einfügen) | – | – | Hauptboard |
| R6 | key_empty_r6_face | key_empty_face | 0.95×0.95 | Brake-red | key_empty_r6_icon · EmbeddedDoc (Delta-Logo) | – | – | Hauptboard |
| R6 | key_entf_r6_face | key_entf_r1_face | 0.95×0.95 | Onyx | key_entf_r6_pixels · Dot-Matrix (Entf) | – | – | Hauptboard |
| R6 | key_exit_r6_face | key_exit_r1_face | 0.95×0.95 | Onyx | key_exit_r6_pixels · Dot-Matrix (Exit/Power-Icon) | – | – | Hauptboard |
| R6 | key_fancy_1_r6_face | key_fancy_1_r6_face | 0.95×0.95 | Onyx | key_fancy_1_r6_pixels · Dot-Matrix (Fancy-Icon 1) | – | – | Zusatzkappen |
| R6 | key_fancy_2_r6_face | key_fancy_2_r6_face | 0.95×0.95 | Onyx | key_fancy_2_r6_pixels · Dot-Matrix (Fancy-Icon 2) | – | – | Zusatzkappen |
| R6 | key_fancy_3_r6_face | key_fancy_3_r6_face | 0.95×0.95 | Onyx | key_fancy_3_r6_pixels · Dot-Matrix (Fancy-Icon 3) | – | – | Zusatzkappen |

### R5 (21 Kappen: 21 Hauptboard, 0 Zusatz)

| Reihe | Face-Node (neu) | alter Name | Größe (U) | Zone | Haupt | Sub | AltGr | Block |
|---|---|---|---|---|---|---|---|---|
| R5 | key_caret_r5_face | key_caret_face | 0.95×0.95 | Snow | key_caret_r5 · "^" Vektor, Ink | key_caret_r5_sub | – | Hauptboard |
| R5 | key_num_1_r5_face | key_num_1_face | 0.95×0.95 | Snow | key_num_1_r5 · "1" Vektor, Ink | key_num_1_r5_sub | – | Hauptboard |
| R5 | key_num_2_r5_face | key_num_2_face | 0.95×0.95 | Snow | key_num_2_r5 · "2" Vektor, Ink | key_num_2_r5_sub | key_num_2_r5_gr | Hauptboard |
| R5 | key_num_3_r5_face | key_num_3_face | 0.95×0.95 | Snow | key_num_3_r5 · "3" Vektor, Ink | key_num_3_r5_sub | key_num_3_r5_gr | Hauptboard |
| R5 | key_num_4_r5_face | key_num_4_face | 0.95×0.95 | Snow | key_num_4_r5 · "4" Vektor, Ink | key_num_4_r5_sub | – | Hauptboard |
| R5 | key_num_5_r5_face | key_num_5_face | 0.95×0.95 | Snow | key_num_5_r5 · "5" Vektor, Ink | key_num_5_r5_sub | – | Hauptboard |
| R5 | key_num_6_r5_face | key_num_6_face | 0.95×0.95 | Snow | key_num_6_r5 · "6" Vektor, Ink | key_num_6_r5_sub | – | Hauptboard |
| R5 | key_num_7_r5_face | key_num_7_face | 0.95×0.95 | Snow | key_num_7_r5 · "7" Vektor, Ink | key_num_7_r5_sub | key_num_7_r5_gr | Hauptboard |
| R5 | key_num_8_r5_face | key_num_8_face | 0.95×0.95 | Snow | key_num_8_r5 · "8" Vektor, Ink | key_num_8_r5_sub | key_num_8_r5_gr | Hauptboard |
| R5 | key_num_9_r5_face | key_num_9_face | 0.95×0.95 | Snow | key_num_9_r5 · "9" Vektor, Ink | key_num_9_r5_sub | key_num_9_r5_gr | Hauptboard |
| R5 | key_num_0_r5_face | key_num_0_face | 0.95×0.95 | Snow | key_num_0_r5 · "0" Vektor, Ink | key_num_0_r5_sub | key_num_0_r5_gr | Hauptboard |
| R5 | key_ss_r5_face | key_ss_face | 0.95×0.95 | Snow | key_ss_r5 · "ß" Vektor, Ink | key_ss_r5_sub | key_ss_r5_gr | Hauptboard |
| R5 | key_acute_r5_face | key_acute_face | 0.95×0.95 | Snow | key_acute_r5 · "´" Vektor, Ink | key_acute_r5_sub | – | Hauptboard |
| R5 | key_backspace_r5_face | key_backspace_face | 1.96×0.95 | Onyx | key_backspace_r5_pixels · Dot-Matrix "⟵" | – | – | Hauptboard |
| R5 | key_einf_r5_face | key_einf_face | 0.95×0.95 | Snow | key_einf_r5_pixels · Dot-Matrix (Einfügen) | – | – | Hauptboard |
| R5 | key_pos1_r5_face | key_pos1_face | 0.95×0.95 | Snow | key_pos1_r5_pixels · Dot-Matrix (Pos1) | – | – | Hauptboard |
| R5 | key_bild_up_r5_face | key_bild_up_face | 0.95×0.95 | Snow | key_bild_up_r5_pixels · Dot-Matrix (Bild↑) | – | – | Hauptboard |
| R5 | key_numlock_r5_face | key_numlock_face | 0.95×0.95 | Onyx | key_numlock_r5_pixels · Dot-Matrix (Numlock) | – | – | Hauptboard |
| R5 | key_numpad_div_r5_face | key_numpad_div_r1_face | 0.95×0.95 | Onyx | key_numpad_div_r5 · "/" Vektor (Snow-Ink) | – | – | Hauptboard |
| R5 | key_numpad_mul_r5_face | key_numpad_mul_r1_face | 0.95×0.95 | Onyx | key_numpad_mul_r5 · "*" Vektor (Snow-Ink) | – | – | Hauptboard |
| R5 | key_numpad_sub_r5_face | key_numpad_sub_r1_face | 0.95×0.95 | Onyx | key_numpad_sub_r5 · "-" Vektor (Snow-Ink) | – | – | Hauptboard |

### R4 (21 Kappen: 20 Hauptboard, 1 Zusatz)

| Reihe | Face-Node (neu) | alter Name | Größe (U) | Zone | Haupt | Sub | AltGr | Block |
|---|---|---|---|---|---|---|---|---|
| R4 | key_tab_r4_face | key_tab_face | 1.46×0.95 | Onyx | key_tab_r4_pixels · Dot-Matrix "↹" | – | – | Hauptboard |
| R4 | key_q_r4_face | key_q_face | 0.95×0.95 | Snow | key_q_r4 · "Q" Vektor, Ink | – | key_q_r4_gr | Hauptboard |
| R4 | key_w_r4_face | key_w_face | 0.95×0.95 | Snow | key_w_r4 · "W" Vektor, Ink | – | – | Hauptboard |
| R4 | key_e_r4_face | key_e_face | 0.95×0.95 | Snow | key_e_r4 · "E" Vektor, Ink | – | key_e_r4_gr | Hauptboard |
| R4 | key_r_r4_face | key_r_face | 0.95×0.95 | Snow | key_r_r4 · "R" Vektor, Ink | – | – | Hauptboard |
| R4 | key_t_r4_face | key_t_face | 0.95×0.95 | Snow | key_t_r4 · "T" Vektor, Ink | – | – | Hauptboard |
| R4 | key_z_r4_face | key_z_face | 0.95×0.95 | Snow | key_z_r4 · "Z" Vektor, Ink | – | – | Hauptboard |
| R4 | key_u_r4_face | key_u_face | 0.95×0.95 | Snow | key_u_r4 · "U" Vektor, Ink | – | – | Hauptboard |
| R4 | key_i_r4_face | key_i_face | 0.95×0.95 | Snow | key_i_r4 · "I" Vektor, Ink | – | – | Hauptboard |
| R4 | key_o_r4_face | key_o_face | 0.95×0.95 | Snow | key_o_r4 · "O" Vektor, Ink | – | – | Hauptboard |
| R4 | key_p_r4_face | key_p_face | 0.95×0.95 | Snow | key_p_r4 · "P" Vektor, Ink | – | – | Hauptboard |
| R4 | key_ue_r4_face | key_ue_face | 0.95×0.95 | Snow | key_ue_r4 · "Ü" Vektor, Ink | – | – | Hauptboard |
| R4 | key_plus_r4_face | key_plus_face | 0.95×0.95 | Snow | key_plus_r4 · "+" Vektor, Ink | key_plus_r4_sub | key_plus_r4_gr | Hauptboard |
| R4 | key_hash_r4_face | key_hash_r4_face | 1.46×0.95 | Ash-Rosé | key_hash_r4 · "#" Vektor, Ink | key_hash_r4_sub | – | Hauptboard |
| R4 | key_entf_r4_face | key_entf_face | 0.95×0.95 | Snow | key_entf_r4_pixels · Dot-Matrix (Entf) | – | – | Hauptboard |
| R4 | key_ende_r4_face | key_ende_face | 0.95×0.95 | Snow | key_ende_r4_pixels · Dot-Matrix (Ende) | – | – | Hauptboard |
| R4 | key_bild_down_r4_face | key_bild_down_face | 0.95×0.95 | Snow | key_bild_down_r4_pixels · Dot-Matrix (Bild↓) | – | – | Hauptboard |
| R4 | key_numpad_7_r4_face | key_numpad_7_face | 0.95×0.95 | Snow | key_numpad_7_r4 · "7" Vektor, Ink | – | – | Hauptboard |
| R4 | key_numpad_8_r4_face | key_numpad_8_face | 0.95×0.95 | Snow | key_numpad_8_r4 · "8" Vektor, Ink | – | – | Hauptboard |
| R4 | key_numpad_9_r4_face | key_numpad_9_face | 0.95×0.95 | Snow | key_numpad_9_r4 · "9" Vektor, Ink | – | – | Hauptboard |
| R4 | key_bild_up_r4_face | key_bild_up_r4_face | 0.95×0.95 | Snow | key_bild_up_r4_pixels · Dot-Matrix (Bild↑) | – | – | Zusatzkappen |

### R3 (23 Kappen: 17 Hauptboard, 6 Zusatz)

| Reihe | Face-Node (neu) | alter Name | Größe (U) | Zone | Haupt | Sub | AltGr | Block |
|---|---|---|---|---|---|---|---|---|
| R4+R3 | key_numpad_plus_r4_r3_face | key_numpad_plus_face | 0.95×1.95 | Onyx | key_numpad_plus_r4_r3 · "+" Vektor (Snow-Ink) | – | – | Hauptboard |
| R3 | key_caps_r3_face | key_caps_face | 1.71×0.95 | Onyx | key_caps_r3_pixels · Dot-Matrix "⇪" | – | – | Hauptboard |
| R3 | key_a_r3_face | key_a_face | 0.95×0.95 | Snow | key_a_r3 · "A" Vektor, Ink | – | – | Hauptboard |
| R3 | key_s_r3_face | key_s_face | 0.95×0.95 | Snow | key_s_r3 · "S" Vektor, Ink | – | – | Hauptboard |
| R3 | key_d_r3_face | key_d_face | 0.95×0.95 | Snow | key_d_r3 · "D" Vektor, Ink | – | – | Hauptboard |
| R3 | key_f_r3_face | key_f_face | 0.95×0.95 | Snow | key_f_r3 · "F" Vektor, Ink | – | – | Hauptboard |
| R3 | key_g_r3_face | key_g_face | 0.95×0.95 | Snow | key_g_r3 · "G" Vektor, Ink | – | – | Hauptboard |
| R3 | key_h_r3_face | key_h_face | 0.95×0.95 | Snow | key_h_r3 · "H" Vektor, Ink | – | – | Hauptboard |
| R3 | key_j_r3_face | key_j_face | 0.95×0.95 | Snow | key_j_r3 · "J" Vektor, Ink | – | – | Hauptboard |
| R3 | key_k_r3_face | key_k_face | 0.95×0.95 | Snow | key_k_r3 · "K" Vektor, Ink | – | – | Hauptboard |
| R3 | key_l_r3_face | key_l_face | 0.95×0.95 | Snow | key_l_r3 · "L" Vektor, Ink | – | – | Hauptboard |
| R3 | key_oe_r3_face | key_oe_face | 0.95×0.95 | Snow | key_oe_r3 · "Ö" Vektor, Ink | – | – | Hauptboard |
| R3 | key_ae_r3_face | key_ae_face | 0.95×0.95 | Snow | key_ae_r3 · "Ä" Vektor, Ink | – | – | Hauptboard |
| R3 | key_enter_r3_face | key_enter_face | 2.21×0.95 | Brake-red | key_enter_r3_pixels · Dot-Matrix "↵" | – | – | Hauptboard |
| R3 | key_numpad_4_r3_face | key_numpad_4_face | 0.95×0.95 | Snow | key_numpad_4_r3 · "4" Vektor, Ink | – | – | Hauptboard |
| R3 | key_numpad_5_r3_face | key_numpad_5_face | 0.95×0.95 | Snow | key_numpad_5_r3 · "5" Vektor, Ink | – | – | Hauptboard |
| R3 | key_numpad_6_r3_face | key_numpad_6_face | 0.95×0.95 | Snow | key_numpad_6_r3 · "6" Vektor, Ink | – | – | Hauptboard |
| R4+R3 | key_ISO_Enter_r4_r3_face | key_ISO_Enter_r3_face | 1.48×1.97 | Brake-red | key_ISO_Enter_r4_r3_pixels · Dot-Matrix "↵" | – | – | Zusatzkappen |
| R3 | key_hash_r3_face | key_hash_r3_face | 0.95×0.95 | Snow | key_hash_r3 · "#" Vektor, Ink | key_hash_r3_sub | – | Zusatzkappen |
| R3 | key_bild_down_r3_face | key_bild_down_r3_face | 0.95×0.95 | Snow | key_bild_down_r3_pixels · Dot-Matrix (Bild↓) | – | – | Zusatzkappen |
| R3 | key_entf_r3_face | key_entf_r3_face | 0.95×0.95 | Snow | key_entf_r3_pixels · Dot-Matrix (Entf) | – | – | Zusatzkappen |
| R3 | key_bild_up_r3_face | key_bild_up_r3_face | 0.95×0.95 | Snow | key_bild_up_r3_pixels · Dot-Matrix (Bild↑) | – | – | Zusatzkappen |
| R3 | key_ende_r3_face | key_ende_r3_face | 0.95×0.95 | Snow | key_ende_r3_pixels · Dot-Matrix (Ende) | – | – | Zusatzkappen |

### R2 (24 Kappen: 16 Hauptboard, 8 Zusatz)

| Reihe | Face-Node (neu) | alter Name | Größe (U) | Zone | Haupt | Sub | AltGr | Block |
|---|---|---|---|---|---|---|---|---|
| R2 | key_shift_l_r2_face | key_shift_l_face | 2.21×0.95 | Onyx | key_shift_l_r2_pixels · Dot-Matrix "⇧" | – | – | Hauptboard |
| R2 | key_y_r2_face | key_y_face | 0.95×0.95 | Snow | key_y_r2 · "Y" Vektor, Ink | – | – | Hauptboard |
| R2 | key_x_r2_face | key_x_face | 0.95×0.95 | Snow | key_x_r2 · "X" Vektor, Ink | – | – | Hauptboard |
| R2 | key_c_r2_face | key_c_face | 0.95×0.95 | Snow | key_c_r2 · "C" Vektor, Ink | – | – | Hauptboard |
| R2 | key_v_r2_face | key_v_face | 0.95×0.95 | Snow | key_v_r2 · "V" Vektor, Ink | – | – | Hauptboard |
| R2 | key_b_r2_face | key_b_face | 0.95×0.95 | Snow | key_b_r2 · "B" Vektor, Ink | – | – | Hauptboard |
| R2 | key_n_r2_face | key_n_face | 0.95×0.95 | Snow | key_n_r2 · "N" Vektor, Ink | – | – | Hauptboard |
| R2 | key_m_r2_face | key_m_face | 0.95×0.95 | Snow | key_m_r2 · "M" Vektor, Ink | – | key_m_r2_gr | Hauptboard |
| R2 | key_semicolon_r2_face | key_semicolon_face | 0.95×0.95 | Snow | key_semicolon_r2 · "," Vektor, Ink | key_semicolon_r2_sub | – | Hauptboard |
| R2 | key_colon_r2_face | key_colon_face | 0.95×0.95 | Snow | key_colon_r2 · "." Vektor, Ink | key_colon_r2_sub | – | Hauptboard |
| R2 | key_dash_r2_face | key_dash_face | 0.95×0.95 | Snow | key_dash_r2 · "-" Vektor, Ink | key_dash_r2_sub | – | Hauptboard |
| R2 | key_shift_r_r2_face | key_shift_r_face | 2.68×0.95 | Onyx | key_shift_r_r2_pixels · Dot-Matrix "⇧" | – | – | Hauptboard |
| R2 | key_arrow_up_r2_face | key_arrow_up_face | 0.95×0.95 | Snow | key_arrow_up_r2_pixels · Dot-Matrix "↑" | – | – | Hauptboard |
| R2 | key_numpad_1_r2_face | key_numpad_1_face | 0.95×0.95 | Snow | key_numpad_1_r2 · "1" Vektor, Ink | – | – | Hauptboard |
| R2 | key_numpad_2_r2_face | key_numpad_2_face | 0.95×0.95 | Snow | key_numpad_2_r2 · "2" Vektor, Ink | – | – | Hauptboard |
| R2 | key_numpad_3_r2_face | key_numpad_3_face | 0.95×0.95 | Snow | key_numpad_3_r2 · "3" Vektor, Ink | – | – | Hauptboard |
| R2 | key_bild_down_r2_face | key_bild_down_r2_face | 0.95×0.95 | Snow | key_bild_down_r2_pixels · Dot-Matrix (Bild↓) | – | – | Zusatzkappen |
| R2 | key_ende_r2_face | key_ende_r2_face | 0.95×0.95 | Snow | key_ende_r2_pixels · Dot-Matrix (Ende) | – | – | Zusatzkappen |
| R2 | key_entf_r2_face | key_entf_r2_face | 0.95×0.95 | Snow | key_entf_r2_pixels · Dot-Matrix (Entf) | – | – | Zusatzkappen |
| R2 | key_1u_shift_r2_face | key_1u_shift_r2_face | 0.95×0.95 | Onyx | key_1u_shift_r2_pixels · Dot-Matrix "⇧" | – | – | Zusatzkappen |
| R2 | key_less_r2_face | key_less_r2_face | 0.95×0.95 | Snow | key_less_r2 · "<" Vektor, Ink | key_less_r2_sub | key_less_r2_gr | Zusatzkappen |
| R2 | key_1.25u_shift_r2_face | key_1.25u_shift_r2_face | 1.18×0.95 | Ash-Rosé | key_1.25u_shift_r2_pixels · Dot-Matrix "⇧" | – | – | Zusatzkappen |
| R2 | key_1.75u_shift_r2_face | key_1.75u_shift_r2_face | 1.71×0.95 | Onyx | key_1.75u_shift_r2_pixels · Dot-Matrix "⇧" | – | – | Zusatzkappen |
| R2 | key_2u_shift_r2_face | key_2u_shift_r2_face | 1.96×0.95 | Onyx | key_2u_shift_r2_pixels · Dot-Matrix "⇧" | – | – | Zusatzkappen |

### R1 (19 Kappen: 14 Hauptboard, 5 Zusatz)

| Reihe | Face-Node (neu) | alter Name | Größe (U) | Zone | Haupt | Sub | AltGr | Block |
|---|---|---|---|---|---|---|---|---|
| R2+R1 | key_numpad_enter_r2_r1_face | key_numpad_enter_face | 0.95×1.95 | Brake-red | key_numpad_enter_r2_r1_pixels · Dot-Matrix "↵" | – | – | Hauptboard |
| R1 | key_ctrl_l_r1_face | key_ctrl_l_face | 1.18×0.95 | Onyx | key_ctrl_l_r1_pixels · Dot-Matrix "STRG" | – | – | Hauptboard |
| R1 | key_win_r1_face | key_win_face | 1.18×0.95 | Onyx | key_win_r1_pixels · Dot-Matrix "WIN" | – | – | Hauptboard |
| R1 | key_alt_r1_face | key_alt_face | 1.18×0.95 | Onyx | key_alt_r1_pixels · Dot-Matrix "ALT" | – | – | Hauptboard |
| R1 | key_space_r1_face | key_space_face | 6.20×0.95 | Snow | key_space_r1_pixels · Dot-Matrix (Delta-Logo/EQ) | – | – | Hauptboard |
| R1 | key_altgr_r1_face | key_altgr_face | 1.18×0.95 | Onyx | key_altgr_r1_pixels · Dot-Matrix "ALT" | – | – | Hauptboard |
| R1 | key_fn_r_r1_face | key_fn_r_face | 1.18×0.95 | Onyx | key_fn_r_r1_pixels · Dot-Matrix "Fn" | – | – | Hauptboard |
| R1 | key_menu_r1_face | key_menu_face | 1.18×0.95 | Ash-Rosé | key_menu_r1_pixels · Dot-Matrix (Menü-Icon) | – | – | Hauptboard |
| R1 | key_ctrl_r_r1_face | key_ctrl_r_face | 1.18×0.95 | Onyx | key_ctrl_r_r1_pixels · Dot-Matrix "STRG" | – | – | Hauptboard |
| R1 | key_arrow_left_r1_face | key_arrow_left_face | 0.95×0.95 | Snow | key_arrow_left_r1_pixels · Dot-Matrix "←" | – | – | Hauptboard |
| R1 | key_arrow_down_r1_face | key_arrow_down_face | 0.95×0.95 | Snow | key_arrow_down_r1_pixels · Dot-Matrix "↓" | – | – | Hauptboard |
| R1 | key_arrow_right_r1_face | key_arrow_right_face | 0.95×0.95 | Snow | key_arrow_right_r1_pixels · Dot-Matrix "→" | – | – | Hauptboard |
| R1 | key_numpad_0_r1_face | key_numpad_0_face | 1.96×0.95 | Snow | key_numpad_0_r1 · "0" Vektor, Ink | – | – | Hauptboard |
| R1 | key_numpad_dot_r1_face | key_numpad_entf_r1_face | 0.95×0.95 | Snow | key_numpad_dot_r1 · "." Vektor, Ink (seit 2026-10-05, vorher key_numpad_entf_r1_pixels · Dot-Matrix Entf; Lage wie key_colon_r2 oben links; Face am 2026-10-05 von key_numpad_entf_r1_face umbenannt) | – | – | Hauptboard |
| R1 | key_numpad_0_1u_r1_face | key_numpad_0_r1_face | 0.95×0.95 | Snow | key_numpad_0_1u_r1 · "0" Vektor, Ink | – | – | Zusatzkappen |
| R1 | key_strg_r1_face | key_strg_r1_face | 0.95×0.95 | Onyx | key_strg_r1_pixels · Dot-Matrix "STRG" | – | – | Zusatzkappen |
| R1 | key_menu_1u_r1_face | key_menu_r1_face | 0.95×0.95 | Onyx | key_menu_1u_r1_pixels · Dot-Matrix (Menü-Icon) | – | – | Zusatzkappen |
| R1 | key_alt_1u_r1_face | key_alt_r1_face | 0.95×0.95 | Onyx | key_alt_1u_r1_pixels · Dot-Matrix "ALT" | – | – | Zusatzkappen |
| R1 | key_fn_r1_face | key_fn_r1_face | 0.95×0.95 | Ash-Rosé | key_fn_r1_pixels · Dot-Matrix "FN" | – | – | Zusatzkappen |

## Kappen über zwei Reihen

| Face-Node (neu) | alter Name | Reihen | Größe (U) | Block |
|---|---|---|---|---|
| key_numpad_plus_r4_r3_face | key_numpad_plus_face | R4+R3 | 0.95×1.95 | Hauptboard |
| key_numpad_enter_r2_r1_face | key_numpad_enter_face | R2+R1 | 0.95×1.95 | Hauptboard |
| key_ISO_Enter_r4_r3_face | key_ISO_Enter_r3_face | R4+R3 | 1.48×1.97 | Zusatzkappen |

## Änderungen gegenüber Inventar 2026-09-28
- Alle Face- und Legenden-Nodes tragen die Reihe im Namen; Kollisionen gelöst über `_1u`: `key_alt_1u_r1`, `key_menu_1u_r1`, `key_numpad_0_1u_r1`.
- Konfliktfälle nach Lage umbenannt: Einfg/Entf/Exit der F-Reihe (alt `_r1`) -> `_r6`, Ziffernblock `/ * -` (alt `_r1`) -> `_r5`.
- `key_numpad_plus` ist Kappe über R4+R3 (altes Inventar: „Zahlenzeile“, falsch).
- ISO-Enter heißt `key_ISO_Enter_r4_r3` und ist im Mapping Zusatzkappe (altes Inventar: Hauptboard/ISO-Block).
- Rechte Win-Taste ist seit 2026-10-01 Fn R (`key_fn_r_r1`, Legende „Fn“, `key_fn_r_r1_pixels`).

## Abgleich offen
- Keine: alle 131 Faces des Mapping sind im alten Inventar vorhanden und umgekehrt (Abgleich über `alt`).

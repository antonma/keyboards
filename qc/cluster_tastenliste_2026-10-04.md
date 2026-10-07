# Tastenliste je Cluster — Werker-QC (Stand 2026-10-05, finaler Schnitt, Alpine 139 / Hello v1.36)

Ersetzt die Fassung vom 2026-10-04 (Stand Alpine 134 / Hello v1.33). Zehn Cluster nach Legendenart, von Anton freigegeben. Maschinenlesbar: `qc/checklist/qs_v3_clusters.json` (diese Datei ist daraus erzeugt).
Quellen: Boards/Bboxen `qc/checklist/img/ref/alpine_139_*` (131 Kappen) und `hello_v136_*` (133 Kappen); Legenden aus `qc/inventory_alpine_2026-10-04.md` bzw. `qc/inventory_hello_2026-09-28.md`.
Reihe (Alpine): R6 = F, R5 = Zahlen, R4 = Tab, R3 = Caps, R2 = Shift, R1 = Strg; Zwei-Reihen-Kappen als `R4+R3` / `R2+R1`, in der Verteilung zur unteren Reihe gezählt.
Zuordnung: ISO-Enter, `<`, `>`, `#`/`'` 1U und 1,5U in Cluster 2 bzw. 7; NumLock in Cluster 6 (nicht 10); Hello `key_hero_3`/`key_hero_4` (Entf-Icons F-Reihe) in Cluster 6; `key_hero_1`/`key_hero_2` (Delta-Logos) in Cluster 8; Ziffernblock-Punkt-Taste in Cluster 10.

## ALPINE (131)

| # | Cluster | Tasten (Node-Name ohne `_face`) | Anzahl | Verteilung nach Reihe |
|---|---|---|---|---|
| 1 | Alpha-Buchstaben (A–Z, Ä Ö Ü) | `key_q_r4`, `key_w_r4`, `key_e_r4`, `key_r_r4`, `key_t_r4`, `key_z_r4`, `key_u_r4`, `key_i_r4`, `key_o_r4`, `key_p_r4`, `key_ue_r4`, `key_a_r3`, `key_s_r3`, `key_d_r3`, `key_f_r3`, `key_g_r3`, `key_h_r3`, `key_j_r3`, `key_k_r3`, `key_l_r3`, `key_oe_r3`, `key_ae_r3`, `key_y_r2`, `key_x_r2`, `key_c_r2`, `key_v_r2`, `key_b_r2`, `key_n_r2`, `key_m_r2` | 29 | R4 11 · R3 11 · R2 7 |
| 2 | Zahlen und Sonderzeichen | `key_caret_r5`, `key_num_1_r5`, `key_num_2_r5`, `key_num_3_r5`, `key_num_4_r5`, `key_num_5_r5`, `key_num_6_r5`, `key_num_7_r5`, `key_num_8_r5`, `key_num_9_r5`, `key_num_0_r5`, `key_ss_r5`, `key_acute_r5`, `key_plus_r4`, `key_hash_r4`, `key_hash_r3`, `key_semicolon_r2`, `key_colon_r2`, `key_dash_r2`, `key_less_r2` | 20 | R5 13 · R4 2 · R3 1 · R2 4 |
| 3 | F-Reihe (F1–F12) | `key_f1_r6`, `key_f2_r6`, `key_f3_r6`, `key_f4_r6`, `key_f5_r6`, `key_f6_r6`, `key_f7_r6`, `key_f8_r6`, `key_f9_r6`, `key_f10_r6`, `key_f11_r6`, `key_f12_r6` | 12 | R6 12 |
| 4 | Mod | `key_backspace_r5`, `key_tab_r4`, `key_caps_r3`, `key_ctrl_l_r1`, `key_win_r1`, `key_alt_r1`, `key_altgr_r1`, `key_fn_r_r1`, `key_menu_r1`, `key_ctrl_r_r1`, `key_strg_r1`, `key_menu_1u_r1`, `key_alt_1u_r1`, `key_fn_r1` | 14 | R5 1 · R4 1 · R3 1 · R1 11 |
| 5 | Shift | `key_shift_l_r2`, `key_shift_r_r2`, `key_1u_shift_r2`, `key_1.25u_shift_r2`, `key_1.75u_shift_r2`, `key_2u_shift_r2` | 6 | R2 6 |
| 6 | Steuerung (inkl. NumLock) | `key_druck_r6`, `key_rollen_r6`, `key_pause_r6`, `key_einf_r6`, `key_entf_r6`, `key_einf_r5`, `key_pos1_r5`, `key_bild_up_r5`, `key_numlock_r5`, `key_entf_r4`, `key_ende_r4`, `key_bild_down_r4`, `key_bild_up_r4`, `key_bild_down_r3`, `key_entf_r3`, `key_bild_up_r3`, `key_ende_r3`, `key_bild_down_r2`, `key_ende_r2`, `key_entf_r2` | 20 | R6 5 · R5 4 · R4 4 · R3 4 · R2 3 |
| 7 | Enter | `key_enter_r3`, `key_ISO_Enter_r4_r3`, `key_numpad_enter_r2_r1` | 3 | R3 2 · R1 1 |
| 8 | Delta-Icon, Esc, Novelty + Leertaste | `key_esc_r6`, `key_empty_r6`, `key_exit_r6`, `key_fancy_1_r6`, `key_fancy_2_r6`, `key_fancy_3_r6`, `key_space_r1` | 7 | R6 6 · R1 1 |
| 9 | Pfeile | `key_arrow_up_r2`, `key_arrow_left_r1`, `key_arrow_down_r1`, `key_arrow_right_r1` | 4 | R2 1 · R1 3 |
| 10 | Ziffernblock (ohne Enter, NumLock; inkl. Punkt) | `key_numpad_div_r5`, `key_numpad_mul_r5`, `key_numpad_sub_r5`, `key_numpad_7_r4`, `key_numpad_8_r4`, `key_numpad_9_r4`, `key_numpad_plus_r4_r3`, `key_numpad_4_r3`, `key_numpad_5_r3`, `key_numpad_6_r3`, `key_numpad_1_r2`, `key_numpad_2_r2`, `key_numpad_3_r2`, `key_numpad_0_r1`, `key_numpad_dot_r1`, `key_numpad_0_1u_r1` | 16 | R5 3 · R4 3 · R3 4 · R2 3 · R1 3 |

Summenprobe Alpine: 29 + 20 + 12 + 14 + 6 + 20 + 3 + 7 + 4 + 16 = 131  (Soll 131, bboxes-JSON 131)

## HELLO (133)

| # | Cluster | Tasten (Node-Name) | Anzahl |
|---|---|---|---|
| 1 | Alpha-Buchstaben (A–Z, Ä Ö Ü) | `key_q_face`, `key_w_face`, `key_e_face`, `key_r_face`, `key_t_face`, `key_z_face`, `key_u_face`, `key_i_face`, `key_o_face`, `key_p_face`, `key_ue_face`, `key_a_face`, `key_s_face`, `key_d_face`, `key_f_face`, `key_g_face`, `key_h_face`, `key_j_face`, `key_k_face`, `key_l_face`, `key_oe_face`, `key_ae_face`, `key_y_face`, `key_x_face`, `key_c_face`, `key_v_face`, `key_b_face`, `key_n_face`, `key_m_face` | 29 |
| 2 | Zahlen und Sonderzeichen | `key_caret_face`, `key_num_1_face`, `key_num_2_face`, `key_num_3_face`, `key_num_4_face`, `key_num_5_face`, `key_num_6_face`, `key_num_7_face`, `key_num_8_face`, `key_num_9_face`, `key_num_0_face`, `key_ss_face`, `key_acute_face`, `key_plus_face`, `key_hash_ansi`, `key_semicolon_face`, `key_colon_face`, `key_dash_face`, `key_hash_face`, `key_less_face` | 20 |
| 3 | F-Reihe (F1–F12) | `key_f1_face`, `key_f2_face`, `key_f3_face`, `key_f4_face`, `key_f5_face`, `key_f6_face`, `key_f7_face`, `key_f8_face`, `key_f9_face`, `key_f10_face`, `key_f11_face`, `key_f12_face` | 12 |
| 4 | Mod | `key_backspace_face`, `key_tab_face`, `key_caps_face`, `key_ctrl_l_face`, `key_win_face`, `key_alt_face`, `key_fn_face`, `key_altgr_face`, `key_ctrl_r_face`, `key_menu_face`, `key_fn_1u_face`, `key_menu_1u_face`, `key_alt_1u_face`, `key_ctrl_1u_face` | 14 |
| 5 | Shift | `key_shift_l_face`, `key_shift_r_2.75_face`, `key_shift_1.75u_face`, `key_shift_1.25u_face`, `key_shift_2u_face`, `key_shift_1u_face_new` | 6 |
| 6 | Steuerung (inkl. NumLock) | `key_hero_3`, `key_hero_4`, `key_druck_face`, `key_pause_face`, `key_rollen_face`, `key_bild_up_face`, `key_bild_down_face`, `key_einf_face`, `key_pos1_face`, `key_ende_face`, `key_entf_face`, `key_numlock_face`, `key_druck_rose_face`, `key_rollen_rose_face`, `key_pause_rose_face` | 15 |
| 7 | Enter | `key_enter_face`, `key_numpad_enter_face`, `key_enter_iso_face` | 3 |
| 8 | Delta-Icon, Esc, Novelty + Leertaste | `key_hero_1`, `key_hero_2`, `key_esc_face`, `key_space_face`, `key_note_face`, `key_disk_face`, `key_eq_face`, `key_dial_face`, `key_mic_face`, `key_note_2_face`, `key_cassette_face`, `key_heart_face`, `key_vol_up_face`, `key_vol_down_face` | 14 |
| 9 | Pfeile | `key_arrow_up_face`, `key_arrow_down_face`, `key_arrow_left_face`, `key_arrow_right_face` | 4 |
| 10 | Ziffernblock (ohne Enter, NumLock; inkl. Punkt) | `key_numpad_div_face`, `key_numpad_mul_face`, `key_numpad_sub_face`, `key_numpad_plus_face`, `key_numpad_7_face`, `key_numpad_8_face`, `key_numpad_9_face`, `key_numpad_4_face`, `key_numpad_5_face`, `key_numpad_6_face`, `key_numpad_1_face`, `key_numpad_2_face`, `key_numpad_3_face`, `key_numpad_0_face`, `key_numpad_dot_face`, `key_numpad_0_1u_face` | 16 |

Summenprobe Hello: 29 + 20 + 12 + 14 + 6 + 15 + 3 + 14 + 4 + 16 = 133  (Soll 133, bboxes-JSON 133)

## Änderungen am Kappenbestand gegenüber der Fassung vom 2026-10-04
- Beide Sets: Ziffernblock-Entf-Kappe entfallen, an ihrer Stelle die Punkt-Taste (Alpine `key_numpad_dot_r1`, Hello `key_numpad_dot_face`), Legende „.“, Cluster 10.
- Hello: `key_numpad_0_1u_face` (1U-Null, Legende „0“) neu in Cluster 10; `key_head_set_face` (Novelty Kopfhörer) entfallen — im neuen bboxes-JSON nicht mehr vorhanden, Namensbestand geprüft.
- Alpine: rechtes Fn heißt `key_fn_r_r1_face` (Cluster 4).
- Alle 131 / 133 Namen des neuen bboxes-JSON sind genau einem Cluster zugeordnet; keine Doppelten, keine Offenen.

## Abweichungen von den erwarteten Zahlen
- Keine, Summenprobe stimmt in beiden Sets.

## Auffälligkeiten / zu klären (aus 28.09. übernommen)
- AltGr-Taste ist in beiden Sets mit „ALT“ beschriftet (nicht „ALT GR“) — Absicht?
- NEU: Hello `key_esc_face` zeigt im Board-Export v1.36 ein Telefon-Icon (Inventar 28.09.: "ESC", Gold) — Absicht? Alpine `key_esc_r6_face` zeigt ein Symbol statt eines lesbaren ESC-Schriftzugs.
- NEU: Strg/Win/Alt/AltGr tragen in beiden Boards Symbole statt der im Inventar genannten Schriftzüge STRG/WIN/ALT (Feld `hinweis` im JSON). Die Anzeige-Legende im JSON folgt dem Inventar.
- Hello hat kein Win rechts; Alpine hat Fn R im Hauptboard und zusätzlich Fn als 1U-Zusatzkappe — Absicht?

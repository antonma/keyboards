# Alpine 135 - Reihen-Zuordnung (STA) und Umbenennungsplan - 2026-10-04

Status: **Vorschlag, nichts umbenannt.** Dokument: `release_alpine_135_2026-10-02` (offene Kopie auf dem Desktop `alpine135_release\`, 1 Snapshot). Methode: `spreadVisibleBox` aller 131 Faces (Layer 底色); Reihe = nächstliegende Zeilen-Guide (`STA F/num/Q/A/Z/mod UP`, Zusatzblock `STA S1..S5 UP`) bzw. R-Beschriftung am linken Rand; Legenden per Bbox-Center-Containment (Marge 15 px). 0 unmatched Legenden, 0 Faces ohne Legende.

Konvention: R6 F-Reihe, R5 Zahlenreihe, R4 Tab-Reihe, R3 Caps-Lock-Reihe, R2 Shift-Reihe, R1 Strg-Reihe. Hauptboard-Beschriftungen (y): R6 777, R5 1073, R4 1305, R3 1537, R2 1770, R1 2002. Zusatzblock: R6 2498, R4 2786, R3 3073, R2 3361, R1 3649.

Legenden-Spalte: alt -> neu (Layer Alphas_Alpine, bei key_empty Layer Images). Nur geänderte Namen sind mit Pfeil gezeigt, unveränderte mit `=`.

## Hauptboard

### R6 F-Reihe (20 Kappen)

| Reihe | Face alt | Face neu | Legenden alt -> neu | Lage | Bemerkung |
|---|---|---|---|---|---|
| R6 | key_esc_face | key_esc_r6_face | key_esc_pixels -> key_esc_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_f1_face | key_f1_r6_face | key_f1_pixels -> key_f1_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_f2_face | key_f2_r6_face | key_f2_pixels -> key_f2_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_f3_face | key_f3_r6_face | key_f3_pixels -> key_f3_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_f4_face | key_f4_r6_face | key_f4_pixels -> key_f4_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_f5_face | key_f5_r6_face | key_f5_pixels -> key_f5_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_f6_face | key_f6_r6_face | key_f6_pixels -> key_f6_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_f7_face | key_f7_r6_face | key_f7_pixels -> key_f7_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_f8_face | key_f8_r6_face | key_f8_pixels -> key_f8_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_f9_face | key_f9_r6_face | key_f9_pixels -> key_f9_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_f10_face | key_f10_r6_face | key_f10_pixels -> key_f10_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_f11_face | key_f11_r6_face | key_f11_pixels -> key_f11_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_f12_face | key_f12_r6_face | key_f12_pixels -> key_f12_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_druck_face | key_druck_r6_face | key_druck_pixels -> key_druck_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_rollen_face | key_rollen_r6_face | key_rollen_pixels -> key_rollen_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_pause_face | key_pause_r6_face | key_pause_pixels -> key_pause_r6_pixels | Hauptboard, y=678 |  |
| R6 | key_einf_r1_face | key_einf_r6_face | key_einf_r1_pixels -> key_einf_r6_pixels | Hauptboard, y=678 | KONFLIKT: vorhandenes _r1, Lage = R6 |
| R6 | key_empty_face | key_empty_r6_face | key_empty_icon -> key_empty_r6_icon | Hauptboard, y=678 |  |
| R6 | key_entf_r1_face | key_entf_r6_face | key_entf_r1_pixels -> key_entf_r6_pixels | Hauptboard, y=678 | KONFLIKT: vorhandenes _r1, Lage = R6 |
| R6 | key_exit_r1_face | key_exit_r6_face | key_exit_r1_pixels -> key_exit_r6_pixels | Hauptboard, y=678 | KONFLIKT: vorhandenes _r1, Lage = R6 |

### R5 Zahlenreihe (21 Kappen)

| Reihe | Face alt | Face neu | Legenden alt -> neu | Lage | Bemerkung |
|---|---|---|---|---|---|
| R5 | key_caret_face | key_caret_r5_face | key_caret -> key_caret_r5<br>key_caret_sub -> key_caret_r5_sub | Hauptboard, y=1000 |  |
| R5 | key_num_1_face | key_num_1_r5_face | key_num_1 -> key_num_1_r5<br>key_num_1_sub -> key_num_1_r5_sub | Hauptboard, y=1000 |  |
| R5 | key_num_2_face | key_num_2_r5_face | key_num_2 -> key_num_2_r5<br>key_num_2_sub -> key_num_2_r5_sub<br>key_num_2_gr -> key_num_2_r5_gr | Hauptboard, y=1000 |  |
| R5 | key_num_3_face | key_num_3_r5_face | key_num_3 -> key_num_3_r5<br>key_num_3_sub -> key_num_3_r5_sub<br>key_num_3_gr -> key_num_3_r5_gr | Hauptboard, y=1000 |  |
| R5 | key_num_4_face | key_num_4_r5_face | key_num_4 -> key_num_4_r5<br>key_num_4_sub -> key_num_4_r5_sub | Hauptboard, y=1000 |  |
| R5 | key_num_5_face | key_num_5_r5_face | key_num_5 -> key_num_5_r5<br>key_num_5_sub -> key_num_5_r5_sub | Hauptboard, y=1000 |  |
| R5 | key_num_6_face | key_num_6_r5_face | key_num_6 -> key_num_6_r5<br>key_num_6_sub -> key_num_6_r5_sub | Hauptboard, y=1000 |  |
| R5 | key_num_7_face | key_num_7_r5_face | key_num_7 -> key_num_7_r5<br>key_num_7_sub -> key_num_7_r5_sub<br>key_num_7_gr -> key_num_7_r5_gr | Hauptboard, y=1000 |  |
| R5 | key_num_8_face | key_num_8_r5_face | key_num_8 -> key_num_8_r5<br>key_num_8_sub -> key_num_8_r5_sub<br>key_num_8_gr -> key_num_8_r5_gr | Hauptboard, y=1000 |  |
| R5 | key_num_9_face | key_num_9_r5_face | key_num_9 -> key_num_9_r5<br>key_num_9_sub -> key_num_9_r5_sub<br>key_num_9_gr -> key_num_9_r5_gr | Hauptboard, y=1000 |  |
| R5 | key_num_0_face | key_num_0_r5_face | key_num_0 -> key_num_0_r5<br>key_num_0_sub -> key_num_0_r5_sub<br>key_num_0_gr -> key_num_0_r5_gr | Hauptboard, y=1000 |  |
| R5 | key_ss_face | key_ss_r5_face | key_ss -> key_ss_r5<br>key_ss_sub -> key_ss_r5_sub<br>key_ss_gr -> key_ss_r5_gr | Hauptboard, y=1000 |  |
| R5 | key_acute_face | key_acute_r5_face | key_acute -> key_acute_r5<br>key_acute_sub -> key_acute_r5_sub | Hauptboard, y=1000 |  |
| R5 | key_backspace_face | key_backspace_r5_face | key_backspace_pixels -> key_backspace_r5_pixels | Hauptboard, y=1000 |  |
| R5 | key_einf_face | key_einf_r5_face | key_einf_pixels -> key_einf_r5_pixels | Hauptboard, y=1000 |  |
| R5 | key_pos1_face | key_pos1_r5_face | key_pos1_pixels -> key_pos1_r5_pixels | Hauptboard, y=1000 |  |
| R5 | key_bild_up_face | key_bild_up_r5_face | key_bild_up_pixels -> key_bild_up_r5_pixels | Hauptboard, y=1000 |  |
| R5 | key_numlock_face | key_numlock_r5_face | key_numlock_pixels -> key_numlock_r5_pixels | Hauptboard, y=1000 |  |
| R5 | key_numpad_div_r1_face | key_numpad_div_r5_face | key_numpad_div_r1 -> key_numpad_div_r5 | Hauptboard, y=1000 | KONFLIKT: vorhandenes _r1, Lage = R5 |
| R5 | key_numpad_mul_r1_face | key_numpad_mul_r5_face | key_numpad_mul_r1 -> key_numpad_mul_r5 | Hauptboard, y=1000 | KONFLIKT: vorhandenes _r1, Lage = R5 |
| R5 | key_numpad_sub_r1_face | key_numpad_sub_r5_face | key_numpad_sub_r1 -> key_numpad_sub_r5 | Hauptboard, y=1000 | KONFLIKT: vorhandenes _r1, Lage = R5 |

### R4 Tab-Reihe (20 Kappen)

| Reihe | Face alt | Face neu | Legenden alt -> neu | Lage | Bemerkung |
|---|---|---|---|---|---|
| R4 | key_tab_face | key_tab_r4_face | key_tab_pixels -> key_tab_r4_pixels | Hauptboard, y=1224 |  |
| R4 | key_q_face | key_q_r4_face | key_q -> key_q_r4<br>key_q_gr -> key_q_r4_gr | Hauptboard, y=1224 |  |
| R4 | key_w_face | key_w_r4_face | key_w -> key_w_r4 | Hauptboard, y=1224 |  |
| R4 | key_e_face | key_e_r4_face | key_e -> key_e_r4<br>key_e_gr -> key_e_r4_gr | Hauptboard, y=1224 |  |
| R4 | key_r_face | key_r_r4_face | key_r -> key_r_r4 | Hauptboard, y=1224 |  |
| R4 | key_t_face | key_t_r4_face | key_t -> key_t_r4 | Hauptboard, y=1224 |  |
| R4 | key_z_face | key_z_r4_face | key_z -> key_z_r4 | Hauptboard, y=1224 |  |
| R4 | key_u_face | key_u_r4_face | key_u -> key_u_r4 | Hauptboard, y=1224 |  |
| R4 | key_i_face | key_i_r4_face | key_i -> key_i_r4 | Hauptboard, y=1224 |  |
| R4 | key_o_face | key_o_r4_face | key_o -> key_o_r4 | Hauptboard, y=1224 |  |
| R4 | key_p_face | key_p_r4_face | key_p -> key_p_r4 | Hauptboard, y=1224 |  |
| R4 | key_ue_face | key_ue_r4_face | key_ue -> key_ue_r4 | Hauptboard, y=1224 |  |
| R4 | key_plus_face | key_plus_r4_face | key_plus -> key_plus_r4<br>key_plus_sub -> key_plus_r4_sub<br>key_plus_gr -> key_plus_r4_gr | Hauptboard, y=1224 |  |
| R4 | key_hash_r4_face | key_hash_r4_face | key_hash_r4 (=)<br>key_hash_r4_sub (=) | Hauptboard, y=1224 | _r4 passt zur Lage |
| R4 | key_entf_face | key_entf_r4_face | key_entf_pixels -> key_entf_r4_pixels | Hauptboard, y=1224 |  |
| R4 | key_ende_face | key_ende_r4_face | key_ende_pixels -> key_ende_r4_pixels | Hauptboard, y=1224 |  |
| R4 | key_bild_down_face | key_bild_down_r4_face | key_bild_down_pixels -> key_bild_down_r4_pixels | Hauptboard, y=1224 |  |
| R4 | key_numpad_7_face | key_numpad_7_r4_face | key_numpad_7 -> key_numpad_7_r4 | Hauptboard, y=1224 |  |
| R4 | key_numpad_8_face | key_numpad_8_r4_face | key_numpad_8 -> key_numpad_8_r4 | Hauptboard, y=1224 |  |
| R4 | key_numpad_9_face | key_numpad_9_r4_face | key_numpad_9 -> key_numpad_9_r4 | Hauptboard, y=1224 |  |

### R3 Caps-Lock-Reihe (17 Kappen)

| Reihe | Face alt | Face neu | Legenden alt -> neu | Lage | Bemerkung |
|---|---|---|---|---|---|
| R3 | key_numpad_plus_face | key_numpad_plus_r3_face | key_numpad_plus -> key_numpad_plus_r3 | Hauptboard, y=1224 | Zwei-Reihen-Kappe R4+R3 -> vorlaeufig untere R3 (Anton entscheidet) |
| R3 | key_caps_face | key_caps_r3_face | key_caps_pixels -> key_caps_r3_pixels | Hauptboard, y=1449 |  |
| R3 | key_a_face | key_a_r3_face | key_a -> key_a_r3 | Hauptboard, y=1449 |  |
| R3 | key_s_face | key_s_r3_face | key_s -> key_s_r3 | Hauptboard, y=1449 |  |
| R3 | key_d_face | key_d_r3_face | key_d -> key_d_r3 | Hauptboard, y=1449 |  |
| R3 | key_f_face | key_f_r3_face | key_f -> key_f_r3 | Hauptboard, y=1449 |  |
| R3 | key_g_face | key_g_r3_face | key_g -> key_g_r3 | Hauptboard, y=1449 |  |
| R3 | key_h_face | key_h_r3_face | key_h -> key_h_r3 | Hauptboard, y=1449 |  |
| R3 | key_j_face | key_j_r3_face | key_j -> key_j_r3 | Hauptboard, y=1449 |  |
| R3 | key_k_face | key_k_r3_face | key_k -> key_k_r3 | Hauptboard, y=1449 |  |
| R3 | key_l_face | key_l_r3_face | key_l -> key_l_r3 | Hauptboard, y=1449 |  |
| R3 | key_oe_face | key_oe_r3_face | key_oe -> key_oe_r3 | Hauptboard, y=1449 |  |
| R3 | key_ae_face | key_ae_r3_face | key_ae -> key_ae_r3 | Hauptboard, y=1449 |  |
| R3 | key_enter_face | key_enter_r3_face | key_enter_pixels -> key_enter_r3_pixels | Hauptboard, y=1449 |  |
| R3 | key_numpad_4_face | key_numpad_4_r3_face | key_numpad_4 -> key_numpad_4_r3 | Hauptboard, y=1449 |  |
| R3 | key_numpad_5_face | key_numpad_5_r3_face | key_numpad_5 -> key_numpad_5_r3 | Hauptboard, y=1449 |  |
| R3 | key_numpad_6_face | key_numpad_6_r3_face | key_numpad_6 -> key_numpad_6_r3 | Hauptboard, y=1449 |  |

### R2 Shift-Reihe (16 Kappen)

| Reihe | Face alt | Face neu | Legenden alt -> neu | Lage | Bemerkung |
|---|---|---|---|---|---|
| R2 | key_shift_l_face | key_shift_l_r2_face | key_shift_l_pixels -> key_shift_l_r2_pixels | Hauptboard, y=1673 |  |
| R2 | key_y_face | key_y_r2_face | key_y -> key_y_r2 | Hauptboard, y=1673 |  |
| R2 | key_x_face | key_x_r2_face | key_x -> key_x_r2 | Hauptboard, y=1673 |  |
| R2 | key_c_face | key_c_r2_face | key_c -> key_c_r2 | Hauptboard, y=1673 |  |
| R2 | key_v_face | key_v_r2_face | key_v -> key_v_r2 | Hauptboard, y=1673 |  |
| R2 | key_b_face | key_b_r2_face | key_b -> key_b_r2 | Hauptboard, y=1673 |  |
| R2 | key_n_face | key_n_r2_face | key_n -> key_n_r2 | Hauptboard, y=1673 |  |
| R2 | key_m_face | key_m_r2_face | key_m -> key_m_r2<br>key_m_gr -> key_m_r2_gr | Hauptboard, y=1673 |  |
| R2 | key_semicolon_face | key_semicolon_r2_face | key_semicolon -> key_semicolon_r2<br>key_semicolon_sub -> key_semicolon_r2_sub | Hauptboard, y=1673 |  |
| R2 | key_colon_face | key_colon_r2_face | key_colon -> key_colon_r2<br>key_colon_sub -> key_colon_r2_sub | Hauptboard, y=1673 |  |
| R2 | key_dash_face | key_dash_r2_face | key_dash -> key_dash_r2<br>key_dash_sub -> key_dash_r2_sub | Hauptboard, y=1673 |  |
| R2 | key_shift_r_face | key_shift_r_r2_face | key_shift_r_pixels -> key_shift_r_r2_pixels | Hauptboard, y=1673 | Seiten-r + Reihe: key_shift_r_r2 |
| R2 | key_arrow_up_face | key_arrow_up_r2_face | key_arrow_up_pixels -> key_arrow_up_r2_pixels | Hauptboard, y=1673 |  |
| R2 | key_numpad_1_face | key_numpad_1_r2_face | key_numpad_1 -> key_numpad_1_r2 | Hauptboard, y=1673 |  |
| R2 | key_numpad_2_face | key_numpad_2_r2_face | key_numpad_2 -> key_numpad_2_r2 | Hauptboard, y=1673 |  |
| R2 | key_numpad_3_face | key_numpad_3_r2_face | key_numpad_3 -> key_numpad_3_r2 | Hauptboard, y=1673 |  |

### R1 Strg-Reihe (14 Kappen)

| Reihe | Face alt | Face neu | Legenden alt -> neu | Lage | Bemerkung |
|---|---|---|---|---|---|
| R1 | key_numpad_enter_face | key_numpad_enter_r1_face | key_numpad_enter_pixels -> key_numpad_enter_r1_pixels | Hauptboard, y=1673 | Zwei-Reihen-Kappe R2+R1 -> vorlaeufig untere R1 (Anton entscheidet) |
| R1 | key_ctrl_l_face | key_ctrl_l_r1_face | key_ctrl_l_pixels -> key_ctrl_l_r1_pixels | Hauptboard, y=1898 |  |
| R1 | key_win_face | key_win_r1_face | key_win_pixels -> key_win_r1_pixels | Hauptboard, y=1898 |  |
| R1 | key_alt_face | key_alt_r1_face | key_alt_pixels -> key_alt_r1_pixels | Hauptboard, y=1898 | KOLLISION mit gleichnamiger Kappe -> Vorschlag Variante |
| R1 | key_space_face | key_space_r1_face | key_space_pixels -> key_space_r1_pixels | Hauptboard, y=1898 |  |
| R1 | key_altgr_face | key_altgr_r1_face | key_altgr_pixels -> key_altgr_r1_pixels | Hauptboard, y=1898 |  |
| R1 | key_fn_r_face | key_fn_r_r1_face | key_fn_r_pixels -> key_fn_r_r1_pixels | Hauptboard, y=1898 | Name key_fn_r = rechte Fn; ergibt key_fn_r_r1 (Seiten-r + Reihe) |
| R1 | key_menu_face | key_menu_r1_face | key_menu_pixels -> key_menu_r1_pixels | Hauptboard, y=1898 | KOLLISION mit gleichnamiger Kappe -> Vorschlag Variante |
| R1 | key_ctrl_r_face | key_ctrl_r_r1_face | key_ctrl_r_pixels -> key_ctrl_r_r1_pixels | Hauptboard, y=1898 | Seiten-r + Reihe: key_ctrl_r_r1 |
| R1 | key_arrow_left_face | key_arrow_left_r1_face | key_arrow_left_pixels -> key_arrow_left_r1_pixels | Hauptboard, y=1898 |  |
| R1 | key_arrow_down_face | key_arrow_down_r1_face | key_arrow_down_pixels -> key_arrow_down_r1_pixels | Hauptboard, y=1898 |  |
| R1 | key_arrow_right_face | key_arrow_right_r1_face | key_arrow_right_pixels -> key_arrow_right_r1_pixels | Hauptboard, y=1898 |  |
| R1 | key_numpad_0_face | key_numpad_0_r1_face | key_numpad_0 -> key_numpad_0_r1 | Hauptboard, y=1898 | KOLLISION mit gleichnamiger Kappe -> Vorschlag Variante |
| R1 | key_numpad_entf_r1_face | key_numpad_entf_r1_face | key_numpad_entf_r1_pixels (=) | Hauptboard, y=1898 | _r1 passt zur Lage |

## Zusatz-/Alternativkappen

### R6 F-Reihe (3 Kappen)

| Reihe | Face alt | Face neu | Legenden alt -> neu | Lage | Bemerkung |
|---|---|---|---|---|---|
| R6 | key_fancy_1_r6_face | key_fancy_1_r6_face | key_fancy_1_r6_pixels (=) | Zusatzblock, y=2423 | _r6 passt zur Lage |
| R6 | key_fancy_2_r6_face | key_fancy_2_r6_face | key_fancy_2_r6_pixels (=) | Zusatzblock, y=2423 | _r6 passt zur Lage |
| R6 | key_fancy_3_r6_face | key_fancy_3_r6_face | key_fancy_3_r6_pixels (=) | Zusatzblock, y=2423 | _r6 passt zur Lage |

### R4 Tab-Reihe (1 Kappen)

| Reihe | Face alt | Face neu | Legenden alt -> neu | Lage | Bemerkung |
|---|---|---|---|---|---|
| R4 | key_bild_up_r4_face | key_bild_up_r4_face | key_bild_up_r4_pixels (=) | Zusatzblock, y=2710 | _r4 passt zur Lage |

### R3 Caps-Lock-Reihe (6 Kappen)

| Reihe | Face alt | Face neu | Legenden alt -> neu | Lage | Bemerkung |
|---|---|---|---|---|---|
| R3 | key_ISO_Enter_r3_face | key_ISO_Enter_r3_face | key_ISO_Enter_r3_pixels (=) | Zusatzblock, y=2758 | _r3 passt zur Lage; Zwei-Reihen-Kappe R4+R3 -> vorlaeufig untere R3 (Anton entscheidet) |
| R3 | key_hash_r3_face | key_hash_r3_face | key_hash_r3 (=)<br>key_hash_r3_sub (=) | Zusatzblock, y=2997 | _r3 passt zur Lage |
| R3 | key_bild_down_r3_face | key_bild_down_r3_face | key_bild_down_r3_pixels (=) | Zusatzblock, y=2997 | _r3 passt zur Lage |
| R3 | key_entf_r3_face | key_entf_r3_face | key_entf_r3_pixels (=) | Zusatzblock, y=2997 | _r3 passt zur Lage |
| R3 | key_bild_up_r3_face | key_bild_up_r3_face | key_bild_up_r3_pixels (=) | Zusatzblock, y=2997 | _r3 passt zur Lage |
| R3 | key_ende_r3_face | key_ende_r3_face | key_ende_r3_pixels (=) | Zusatzblock, y=2997 | _r3 passt zur Lage |

### R2 Shift-Reihe (8 Kappen)

| Reihe | Face alt | Face neu | Legenden alt -> neu | Lage | Bemerkung |
|---|---|---|---|---|---|
| R2 | key_bild_down_r2_face | key_bild_down_r2_face | key_bild_down_r2_pixels (=) | Zusatzblock, y=3278 | _r2 passt zur Lage |
| R2 | key_ende_r2_face | key_ende_r2_face | key_ende_r2_pixels (=) | Zusatzblock, y=3278 | _r2 passt zur Lage |
| R2 | key_entf_r2_face | key_entf_r2_face | key_entf_r2_pixels (=) | Zusatzblock, y=3278 | _r2 passt zur Lage |
| R2 | key_1u_shift_r2_face | key_1u_shift_r2_face | key_1u_shift_r2_pixels (=) | Zusatzblock, y=3278 | _r2 passt zur Lage |
| R2 | key_less_r2_face | key_less_r2_face | key_less_r2 (=)<br>key_less_r2_sub (=)<br>key_less_r2_gr (=) | Zusatzblock, y=3278 | _r2 passt zur Lage |
| R2 | key_1.25u_shift_r2_face | key_1.25u_shift_r2_face | key_1.25u_shift_r2_pixels (=) | Zusatzblock, y=3278 | _r2 passt zur Lage |
| R2 | key_1.75u_shift_r2_face | key_1.75u_shift_r2_face | key_1.75u_shift_r2_pixels (=) | Zusatzblock, y=3278 | _r2 passt zur Lage |
| R2 | key_2u_shift_r2_face | key_2u_shift_r2_face | key_2u_shift_r2_pixels (=) | Zusatzblock, y=3278 | _r2 passt zur Lage |

### R1 Strg-Reihe (5 Kappen)

| Reihe | Face alt | Face neu | Legenden alt -> neu | Lage | Bemerkung |
|---|---|---|---|---|---|
| R1 | key_numpad_0_r1_face | key_numpad_0_b_r1_face | key_numpad_0_r1 -> key_numpad_0_b_r1 | Zusatzblock, y=3568 | _r1 passt zur Lage; KOLLISION mit gleichnamiger Kappe -> Vorschlag Variante |
| R1 | key_strg_r1_face | key_strg_r1_face | key_strg_r1_pixels (=) | Zusatzblock, y=3568 | _r1 passt zur Lage |
| R1 | key_menu_r1_face | key_menu_b_r1_face | key_menu_r1_pixels -> key_menu_b_r1_pixels | Zusatzblock, y=3568 | _r1 passt zur Lage; KOLLISION mit gleichnamiger Kappe -> Vorschlag Variante |
| R1 | key_alt_r1_face | key_alt_b_r1_face | key_alt_r1_pixels -> key_alt_b_r1_pixels | Zusatzblock, y=3568 | _r1 passt zur Lage; KOLLISION mit gleichnamiger Kappe -> Vorschlag Variante |
| R1 | key_fn_r1_face | key_fn_r1_face | key_fn_r1_pixels (=) | Zusatzblock, y=3568 | _r1 passt zur Lage |

## Konflikte (vorhandenes _rN passt nicht zur Lage)

| Kappe | vorhanden | tatsächliche Lage | R-Beschriftung / Guide |
|---|---|---|---|
| key_einf_r1 | _r1 | R6 (F-Reihe), y=678, Hauptboard | R6-Beschriftung y~777, Guide STA F UP |
| key_entf_r1 | _r1 | R6 (F-Reihe), y=678, Hauptboard | R6-Beschriftung y~777, Guide STA F UP |
| key_exit_r1 | _r1 | R6 (F-Reihe), y=678, Hauptboard | R6-Beschriftung y~777, Guide STA F UP |
| key_numpad_div_r1 | _r1 | R5 (Zahlenreihe), y=1000, Hauptboard | R5-Beschriftung y~1073, Guide STA num UP |
| key_numpad_mul_r1 | _r1 | R5 (Zahlenreihe), y=1000, Hauptboard | R5-Beschriftung y~1073, Guide STA num UP |
| key_numpad_sub_r1 | _r1 | R5 (Zahlenreihe), y=1000, Hauptboard | R5-Beschriftung y~1073, Guide STA num UP |

Nicht bestätigt aus dem Verdacht: key_numpad_entf_r1 (Hauptboard y=1898, R1) und key_numpad_0_r1 (Zusatzblock y=3568, R1) passen zur Lage.

## Kollisionen

- `key_alt_r1` würde doppelt vergeben: key_alt (Hauptboard), key_alt_r1 (Zusatz). Vorschlag: Zusatzkappe -> `key_alt_b_r1` (Variantenmarker `_b` vor der Reihe, damit `_rN` am Ende parsbar bleibt). **Anton entscheidet.**
- `key_menu_r1` würde doppelt vergeben: key_menu (Hauptboard), key_menu_r1 (Zusatz). Vorschlag: Zusatzkappe -> `key_menu_b_r1` (Variantenmarker `_b` vor der Reihe, damit `_rN` am Ende parsbar bleibt). **Anton entscheidet.**
- `key_numpad_0_r1` würde doppelt vergeben: key_numpad_0 (Hauptboard), key_numpad_0_r1 (Zusatz). Vorschlag: Zusatzkappe -> `key_numpad_0_b_r1` (Variantenmarker `_b` vor der Reihe, damit `_rN` am Ende parsbar bleibt). **Anton entscheidet.**

## Zwei-Reihen-Kappen (vorläufig untere Reihe, Anton entscheidet)

- key_numpad_plus: R4+R3 (Face y=1224, Höhe 439) -> key_numpad_plus_r3 (Inventar sagte fälschlich "Zahlenzeile")
- key_numpad_enter: R2+R1 (Face y=1673, Höhe 439) -> key_numpad_enter_r1
- key_ISO_Enter_r3 (Zusatzblock): R4+R3 (Face y=2758, Höhe 443; Top 48 px unter R4-Zeile, Unterkante 10 px über R3-Unterkante) -> bleibt key_ISO_Enter_r3

## Weitere Node-Gruppen mit Kappen-Namen

- Layer Helpers / Container `STA_mitte`: 132 Kinder = 129 `key_<stem>_mitte` + 2 unregelmäßige (`key_enter_top_mitte` = Mitte von key_hash_r4, `key_win_r_mitte` = Mitte von key_fn_r, stale Namen) + 1 `guide_2_x3458_y258`.
- Layer Helpers / Container `STA_links_rechts`: 264 Kinder = 258 `_links`/`_rechts` (129 Kappen x 2) + 4 unregelmäßige (`key_enter_top_links/_rechts`, `key_win_r_links/_rechts`) + 2 `guide_*`.
- Layer Helpers lose Nodes `ENTER <enter|ISO_Enter_r3|numpad_enter> <Label UP|Mid|DOWN>`: 9 Stück (Namensteil ohne `key_`).
- Zeilen-Guides `STA F|num|Q|A|Z|mod|S1..S5 UP/Label UP/Mid/DOWN` (44) und `mod_align_line`: tragen keine Kappen-Namen.
- Layer 键帽: nur `keycap_art_1..4` (Board-Overlays), kein `*_kontur_*`, keine Kappen-Namen. Layer 文字说明 (482 Nodes) und Layer-Rahmen: komplett unbenannt. Kein 定位-Layer in dieser Datei.
- Namen in Kind-Nodes (Dot-Matrix-Container, Gruppen) wurden stichprobenhaft nicht auf Kappen-Namen gefunden (668 benannte von 8208 Nachfahren in Helpers/Alphas/Images/键帽, davon 446 mit "key").

Helper-Umbenennung (mitte/links/rechts, ENTER) steht vollständig im JSON unter `rename_helper_STA` und `rename_helper_ENTER`.

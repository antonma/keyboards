# Legendenposition-Messung — Hello_MOA_v1.3 & Alpine-133 (Release-Dateien)

Messauftrag, read-only. Keine Änderung/Speicherung an den Dokumenten.

## Methode

- Werkzeug: Affinity SDK (`spreadVisibleBox`, read-only), pro Cap: Face-Node (Basisfarbe/Kappenoberfläche)
  vs. Legenden-Node (Haupt/Sub/AltGr/Icon).
- **Face-Definition:** die `*_face`-PolyCurveNode je Cap im Basisfarben-Layer (Hello: `底层`;
  Alpine: `底色`). Das ist die Kappen-Oberfläche exakt wie im CLAUDE.md-Modell (ein Vektorpfad
  pro Taste), nicht die 3D-Unwrap-Box (`定位框`, die wird nicht verwendet).
- **px→mm:** beide Dateien 300 dpi → Faktor `300/25.4 = 11.811023622 px/mm`.
- Gemessene Größen je Cap: `topD/leftD/rightD/botD` = Abstand Legenden-Bbox zu den vier
  Face-Rändern (mm, positiv = Legende innerhalb der Face); `h` = Legendenhöhe (Bbox-Höhe, mm);
  `dx/dy` = Versatz Legenden-Mitte zu Face-Mitte (mm, + = rechts/unten).
- Cluster 2 zusätzlich: `dxMain/dyMain` = Versatz zur Mitte des zugehörigen Hauptzeichens (mm),
  `hRatio` = Höhe Sub bzw. AltGr / Höhe Main.
- Anker wurde NICHT aus Notes übernommen, sondern aus der Bounding-Box-Geometrie abgeleitet:
  konstantes `topD` + `leftD==rightD` (dx≈0) ⇒ TC (top-center); konstantes `topD` + `leftD`
  ⇒ TL (top-left); konstantes `botD`+`rightD` bzw. `botD`+`leftD` ⇒ entsprechend BR/BL.
- Ausreißer-Regel wie beauftragt (>0.3 mm Positionsabweichung vom Cluster-Median, >5 % Höhe)
  wurde auf ALLE vier Randabstände angewendet; das erzeugt in Cluster 1 und 3 sehr viele
  "Treffer", weil leftD/rightD dort NICHT die Ankerdimension sind, sondern mit der Glyphbreite
  variieren (Ziffer vs. Buchstabe vs. Wortlegende). Das ist eine Methode-Grenze, kein Formfehler.
  Im Abschnitt "Echte Ausreißer" ist deshalb zusätzlich auf die tatsächliche Ankerdimension
  gefiltert.

---

## SET 1 — Hello_MOA_v1.3 (`templates/release/release_hello_moa_v1.3_2026-09-23.af`, Commit 3d2712a)

Layer: `底层` (Face) / `Alphas_MOA` (Legenden). Familie: MOA.

### Cluster 1 — Hauptzeichen (n=75; Buchstaben, Umlaute, Ziffern, Sonderzeichen, F-Reihe als Text)

Anker: **TC (top-center)** für Buchstaben/Umlaute/Numpad-Ziffern (leftD=rightD, dx≈0, topD≈4.860 mm
konstant). Zahlenreihe-Mains und Sonderzeichen (`#^´<-;:+`) sind dagegen **TL-versetzt**
(leftD≈5.29 mm konstant, rightD variiert — Platz für Sub/AltGr rechts). F-Reihe eigene Zeile
(topD≈4.564 mm, h≈8.805 mm — Wortlegenden "F1".."F12").

| Größe | Median | Min | Max |
|---|---|---|---|
| topD | 4.860 mm | 4.564 mm (F-Reihe) | 5.409 mm (numpad_sub) |
| leftD | 7.084 mm | 4.729 mm | 16.995 mm |
| rightD | 7.676 mm | 4.729 mm | 16.995 mm |
| botD | 9.297 mm | 4.898 mm | 29.811 mm (numpad_plus, 2u) |
| h (Höhe) | 4.110 mm | 1.009 mm (numpad_sub) | 8.805 mm (F-Reihe) |
| dx (Mitteversatz h.) | 0.000 mm | −3.157 mm | 0.000 mm |
| dy (Mitteversatz v.) | −2.218 mm | −12.475 mm (numpad_plus) | −0.167 mm (F-Reihe) |

Volltabelle (Name\|topD\|leftD\|rightD\|botD\|h\|dx\|dy, mm):
```
key_q|4.860|7.054|7.054|8.478|4.926|-0.000|-1.809
key_w|4.860|6.495|6.495|9.297|4.107|0.000|-2.218
key_e|4.860|7.634|7.634|9.271|4.133|-0.000|-2.205
key_r|4.860|7.396|7.396|9.279|4.124|-0.000|-2.210
key_t|4.860|7.594|7.594|9.256|4.147|-0.000|-2.198
key_z|4.860|7.699|7.699|9.239|4.165|0.000|-2.189
key_u|4.860|7.360|7.360|9.236|4.168|0.000|-2.188
key_i|4.860|8.498|8.498|9.291|4.112|0.000|-2.216
key_o|4.860|7.054|7.054|9.099|4.305|-0.000|-2.119
key_p|4.860|7.377|7.377|9.294|4.110|0.000|-2.217
key_a|4.860|7.084|7.084|9.221|4.182|0.000|-2.181
key_s|4.860|8.068|8.068|9.040|4.363|-0.000|-2.090
key_d|4.860|7.236|7.236|9.291|4.112|-0.000|-2.216
key_f|4.860|7.613|7.613|9.233|4.171|-0.000|-2.186
key_g|4.860|7.160|7.160|9.145|4.258|-0.000|-2.143
key_h|4.860|7.178|7.178|9.297|4.107|0.000|-2.218
key_j|4.860|8.284|8.284|8.615|4.789|-0.000|-1.877
key_k|4.860|7.338|7.338|9.285|4.118|0.000|-2.213
key_l|4.860|7.676|7.676|9.268|4.136|0.000|-2.204
key_y|4.860|7.371|7.371|9.300|4.107|-0.000|-2.220
key_x|4.860|7.478|7.478|9.297|4.110|-0.000|-2.219
key_c|4.860|7.376|7.376|9.119|4.287|-0.000|-2.130
key_v|4.860|7.354|7.354|9.306|4.101|0.000|-2.223
key_b|4.860|7.405|7.405|9.271|4.136|-0.000|-2.205
key_n|4.860|7.182|7.182|9.248|4.159|0.000|-2.194
key_m|4.860|6.959|6.959|9.230|4.177|0.000|-2.185
key_ue|4.858|7.361|7.361|8.136|5.270|0.000|-1.639
key_ae|4.860|7.084|7.084|8.073|5.331|0.000|-1.606
key_oe|4.860|7.054|7.054|8.029|5.374|-0.000|-1.585
key_ss|4.860|5.292|10.791|10.094|3.310|-2.750|-2.617
key_esc|4.917|4.731|4.731|5.252|8.098|0.000|-0.167
key_num_1|4.860|5.292|11.558|10.092|3.312|-3.133|-2.616
key_num_2|4.860|5.292|10.299|10.087|3.317|-2.504|-2.613
key_num_3|4.860|5.292|10.519|10.092|3.312|-2.614|-2.616
key_num_4|4.860|5.292|10.213|10.060|3.343|-2.461|-2.600
key_num_5|4.860|5.292|10.477|10.107|3.296|-2.593|-2.624
key_num_6|4.860|5.292|10.223|10.076|3.327|-2.466|-2.608
key_num_7|4.860|5.292|10.519|10.076|3.327|-2.614|-2.608
key_num_8|4.860|5.292|10.454|10.060|3.343|-2.581|-2.600
key_num_9|4.860|5.292|10.213|10.045|3.359|-2.461|-2.592
key_num_0|4.860|5.292|9.849|10.087|3.317|-2.278|-2.613
key_numpad_0|4.860|16.995|16.995|10.090|3.317|0.000|-2.615
key_numpad_1|4.860|8.423|8.423|10.095|3.312|0.000|-2.618
key_numpad_2|4.860|7.797|7.797|10.090|3.317|0.000|-2.615
key_numpad_3|4.860|7.905|7.905|10.095|3.312|-0.000|-2.618
key_numpad_4|4.860|7.752|7.752|10.060|3.343|0.000|-2.600
key_numpad_5|4.860|7.886|7.886|10.107|3.296|0.000|-2.624
key_numpad_6|4.860|7.757|7.757|10.076|3.327|0.000|-2.608
key_numpad_7|4.860|7.905|7.905|10.076|3.327|0.000|-2.608
key_numpad_8|4.860|7.875|7.875|10.060|3.343|0.000|-2.600
key_numpad_9|4.860|7.752|7.752|10.045|3.359|-0.000|-2.592
key_numpad_div|4.860|8.407|8.407|9.711|3.693|0.000|-2.426
key_numpad_mul|4.860|8.101|8.101|11.297|2.106|0.000|-3.219
key_numpad_plus|4.860|7.965|7.965|29.811|2.442|0.000|-12.475
key_numpad_sub|5.409|8.179|8.179|11.846|1.009|0.000|-3.219
key_hash|4.858|5.292|9.576|9.299|4.106|-2.142|-2.221
key_caret|4.860|5.292|10.093|11.218|2.186|-2.401|-3.179
key_acute|4.860|5.292|11.211|12.214|1.189|-2.960|-3.677
key_less|4.858|5.292|10.917|10.424|2.982|-2.813|-2.783
key_dash|4.860|5.292|10.853|12.285|1.122|-2.781|-3.712
key_semicolon|4.860|5.292|11.412|11.524|1.883|-3.060|-3.332
key_colon|4.860|5.292|11.605|12.017|1.390|-3.157|-3.578
key_plus|4.860|5.292|10.375|10.687|2.716|-2.542|-2.914
key_f1|4.564|4.729|4.729|4.898|8.805|-0.000|-0.167
key_f2|4.564|4.729|4.729|4.898|8.805|-0.000|-0.167
key_f3|4.564|4.731|4.731|4.898|8.805|-0.000|-0.167
key_f4|4.564|4.729|4.729|4.898|8.805|-0.000|-0.167
key_f5|4.564|4.731|4.731|4.898|8.805|-0.000|-0.167
key_f6|4.564|4.729|4.729|4.898|8.805|-0.000|-0.167
key_f7|4.564|4.729|4.729|4.898|8.805|-0.000|-0.167
key_f8|4.564|4.729|4.729|4.898|8.805|-0.000|-0.167
key_f9|4.564|4.731|4.731|4.898|8.805|-0.000|-0.167
key_f10|4.564|4.729|4.729|4.898|8.805|-0.000|-0.167
key_f11|4.564|4.729|4.729|4.898|8.805|-0.000|-0.167
key_f12|4.564|4.731|4.731|4.898|8.805|-0.000|-0.167
```

**Echte Ausreißer (>0.3 mm auf der Ankerdimension `topD`, TC-Gruppe):** keine — `topD` liegt bei
allen Buchstaben/Umlauten/Ziffern konstant bei 4.858–4.860 mm. Einzige Abweichung: `key_esc`
(4.917 mm, +0.06 mm — geringfügig, eigene Sonderform) und `key_numpad_sub` (5.409 mm, +0.55 mm
gegenüber 4.860 mm — echter Ausreißer, dazu extrem geringe Höhe 1.009 mm, wirkt wie eine
verkürzte/verschobene Legende, sollte Anton/Builder ansehen).

### Cluster 2 — Mehrfachbelegung (Subs n=19, AltGr n=12)

**Subs** (Median-Anker relativ zur Face: topD≈4.860 mm, leftD≈11.18 mm, rightD≈5.29 mm konstant
→ TR-artig, rechts oben in der Zelle):

| Größe | Median | Min | Max |
|---|---|---|---|
| topD | 4.860 mm | 4.858 mm | 4.871 mm |
| leftD | 11.176 mm | 9.244 mm | 12.129 mm |
| rightD | 5.292 mm | 5.292 mm | 5.407 mm |
| botD | 10.391 mm | 9.746 mm | 12.655 mm |
| h | 3.016 mm | 0.752 mm (dash_sub) | 3.646 mm |
| dxMain | 5.415 mm | 4.557 mm | 6.539 mm |
| dyMain | −0.008 mm | −1.305 mm (hash_sub) | 0.566 mm |
| hRatio (Sub/Main) | ~1.00 (Ziffern) | 0.364 (hash_sub) | 1.694 (colon_sub) |

```
key_num_0_sub|4.860|10.755|5.292|11.727|1.677|2.732|-3.433|dxMain=5.010|dyMain=-0.820|hRatio=0.506
key_num_1_sub|4.860|12.104|5.292|10.093|3.310|3.406|-2.616|dxMain=6.539|dyMain=-0.000|hRatio=1.000
key_num_2_sub|4.860|11.229|5.292|12.067|1.336|2.969|-3.604|dxMain=5.473|dyMain=-0.990|hRatio=0.403
key_num_3_sub|4.860|11.176|5.292|10.093|3.310|2.942|-2.616|dxMain=5.556|dyMain=-0.000|hRatio=1.000
key_num_4_sub|4.871|10.925|5.292|9.746|3.646|2.817|-2.437|dxMain=5.277|dyMain=0.163|hRatio=1.091
key_num_5_sub|4.860|9.244|5.315|10.052|3.351|1.964|-2.596|dxMain=4.557|dyMain=0.028|hRatio=1.017
key_num_6_sub|4.860|10.007|5.292|10.092|3.312|2.358|-2.616|dxMain=4.823|dyMain=-0.008|hRatio=0.995
key_num_7_sub|4.860|11.673|5.292|10.093|3.310|3.191|-2.616|dxMain=5.805|dyMain=-0.008|hRatio=0.995
key_num_8_sub|4.860|11.756|5.292|10.093|3.310|3.232|-2.616|dxMain=5.813|dyMain=-0.016|hRatio=0.990
key_num_9_sub|4.860|11.757|5.292|10.093|3.310|3.233|-2.616|dxMain=5.693|dyMain=-0.024|hRatio=0.986
key_ss_sub|4.860|10.739|5.407|10.087|3.316|2.666|-2.614|dxMain=5.415|dyMain=0.003|hRatio=1.002
key_plus_sub|4.860|10.910|5.292|11.297|2.106|2.809|-3.218|dxMain=5.351|dyMain=-0.305|hRatio=0.775
key_hash_sub|4.858|12.129|5.292|11.910|1.496|3.419|-3.526|dxMain=5.561|dyMain=-1.305|hRatio=0.364
key_caret_sub|4.860|11.081|5.292|11.407|1.996|2.895|-3.274|dxMain=5.295|dyMain=-0.095|hRatio=0.913
key_acute_sub|4.860|11.211|5.292|12.208|1.195|2.960|-3.674|dxMain=5.920|dyMain=0.003|hRatio=1.005
key_less_sub|4.858|10.923|5.292|10.424|2.982|2.816|-2.783|dxMain=5.629|dyMain=0.000|hRatio=1.000
key_semicolon_sub|4.860|11.633|5.292|10.391|3.016|3.171|-2.766|dxMain=6.231|dyMain=0.566|hRatio=1.602
key_colon_sub|4.860|11.924|5.292|11.051|2.355|3.316|-3.096|dxMain=6.473|dyMain=0.483|hRatio=1.694
key_dash_sub|4.860|10.422|5.292|12.655|0.752|2.565|-3.897|dxMain=5.346|dyMain=-0.185|hRatio=0.670
```

**AltGr** (topD/leftD als Anker, konstant je Zahlenreihe: 9.762–9.765 mm / rightD/botD konstant
5.19 mm — AltGr sitzt oben-rechts in der Zelle, unabhängig von der Zeile):

| Größe | Median | Min | Max |
|---|---|---|---|
| topD | 9.764 mm | 9.762 mm | 11.859 mm (plus_gr) |
| leftD | 11.631 mm | 10.137 mm | 12.431 mm |
| rightD | 5.292 mm | 5.292 mm | 5.292 mm |
| botD | 5.191 mm | 5.183 mm | 5.194 mm |
| h | 3.308 mm | 1.214 mm (plus_gr) | 3.316 mm |
| dxMain | 5.315 mm (Median über alle) | 2.423 mm (q_gr, gleicher Buchstabe) | 6.382 mm |
| dyMain | 4.807 mm | 4.096 mm | 6.248 mm |
| hRatio | ~0.86 (Ziffern ~0.99) | 0.447 (plus_gr) | 1.110 (less_gr) |

```
key_num_2_gr|11.345|11.446|5.292|5.191|1.727|3.077|3.077|dxMain=5.581|dyMain=5.690|hRatio=0.521
key_num_3_gr|11.314|11.526|5.292|5.191|1.758|3.117|3.062|dxMain=5.731|dyMain=5.678|hRatio=0.531
key_ss_gr|9.764|11.760|5.292|5.183|3.316|3.234|2.291|dxMain=5.984|dyMain=4.908|hRatio=1.002
key_e_gr|10.238|11.077|5.292|5.191|2.835|2.893|2.523|dxMain=2.893|dyMain=4.729|hRatio=0.686
key_plus_gr|11.859|10.517|5.292|5.191|1.214|2.613|3.334|dxMain=5.154|dyMain=6.248|hRatio=0.447
key_q_gr|9.765|10.137|5.292|5.191|3.307|2.423|2.287|dxMain=2.423|dyMain=4.096|hRatio=0.671
key_num_7_gr|9.762|11.788|5.292|5.191|3.310|3.248|2.286|dxMain=5.862|dyMain=4.894|hRatio=0.995
key_num_8_gr|9.762|11.737|5.292|5.191|3.310|3.223|2.286|dxMain=5.804|dyMain=4.886|hRatio=0.990
key_num_9_gr|9.762|11.739|5.292|5.191|3.310|3.224|2.286|dxMain=5.684|dyMain=4.878|hRatio=0.986
key_num_0_gr|9.762|11.790|5.292|5.191|3.310|3.249|2.286|dxMain=5.528|dyMain=4.899|hRatio=0.998
key_less_gr|9.762|12.431|5.292|5.191|3.310|3.570|2.285|dxMain=6.382|dyMain=5.068|hRatio=1.110
key_m_gr|10.067|11.148|5.292|5.194|3.005|2.928|2.437|dxMain=2.928|dyMain=4.622|hRatio=0.720
```

**Echte Ausreißer Cluster 2 Hello:** `key_num_2_gr` und `key_num_3_gr` (topD 11.31–11.35 mm statt
9.76 mm, ~+1.55 mm, h nur 1.73–1.76 mm — hochgestellte ² ³-Glyphen sitzen bewusst höher/kleiner,
plausibel typografisch, aber deutlich außerhalb der Zeilen-Konstante); `key_plus_gr` (topD
11.86 mm, +2.1 mm, h nur 1.21 mm). Bei den Subs: `key_dash_sub` (h 0.752 mm, kleinster Wert im
Cluster) und `key_hash_sub`/`key_num_0_sub`/`key_num_2_sub` (hRatio 0.36–0.51, deutlich kleiner
als das Hauptzeichen) — bei Bindestrich/Minus als Sub ist eine geringe Höhe typografisch normal
(waagerechter Strich), kein Positionsfehler.

### Cluster 3 — Icons (n=41: Modifier, Nav, Pfeile, Enter/Tab/Caps/Backspace)

Anker: **TC**, konstant `topD=4.564 mm`, `h=8.805 mm` für praktisch alle Icons (Ausnahme:
`key_enter_iso` topD 5.165 mm wegen L-Form, `key_numpad_enter` topD 14.153 mm — 2u-Ring-Form).

| Größe | Median | Min | Max |
|---|---|---|---|
| topD | 4.564 mm | 4.564 mm | 14.153 mm (numpad_enter) |
| leftD | 4.731 mm | 4.574 mm | 21.303 mm (shift_r, breite Taste) |
| rightD | 4.731 mm | 4.574 mm | 26.115 mm (shift_l) |
| botD | 4.895 mm | 4.894 mm | 25.503 mm (enter_iso) |
| h | 8.805 mm | 8.805 mm | 8.805 mm |
| dx | 0.000 mm | −9.497 mm (shift_l, asymmetrische Taste) | 0.000 mm |
| dy | −0.166 mm | −10.169 mm (enter_iso) | 0.000 mm |

```
key_ctrl_l|4.565|7.120|7.121|4.896|8.805|-0.000|-0.165
key_ctrl_r|4.564|7.123|7.123|4.898|8.805|-0.000|-0.167
key_ctrl_1u|4.564|4.731|4.731|4.894|8.805|-0.000|-0.165
key_alt|4.564|7.121|7.121|4.898|8.805|-0.000|-0.167
key_alt_1u|4.564|4.731|4.731|4.895|8.805|-0.000|-0.166
key_altgr|4.564|7.121|7.121|4.898|8.805|-0.000|-0.167
key_menu|4.564|7.121|7.121|4.898|8.805|-0.000|-0.167
key_menu_1u|4.564|4.729|4.729|4.895|8.805|-0.000|-0.166
key_win|4.564|7.121|7.121|4.898|8.805|-0.000|-0.167
key_shift_l|4.564|7.120|26.115|4.895|8.805|-9.497|-0.166
key_shift_r|4.564|21.303|21.303|4.895|8.805|0.000|-0.166
key_shift_1.25u|4.564|7.121|7.121|4.898|8.805|-0.000|-0.167
key_shift_1.75u|4.564|11.772|11.772|4.894|8.805|0.000|-0.165
key_shift_2u|4.564|14.153|14.153|4.894|8.805|0.000|-0.165
key_shift_1u_new|4.564|4.731|4.731|4.895|8.805|-0.000|-0.166
key_caps|4.564|7.120|16.480|4.898|8.805|-4.680|-0.167
key_fn|4.564|7.121|7.121|4.898|8.805|-0.000|-0.167
key_fn_1u|4.564|4.729|4.729|4.895|8.805|0.000|-0.166
key_backspace|4.564|13.999|13.999|4.894|8.805|-0.000|-0.165
key_tab|4.564|7.120|11.855|4.894|8.805|-2.367|-0.165
key_enter|4.564|16.618|16.618|4.894|8.805|0.000|-0.165
key_enter_iso|5.165|10.315|10.315|25.503|8.805|0.000|-10.169
key_numpad_enter|14.153|4.729|4.729|14.153|8.805|0.000|0.000
key_arrow_up|4.564|4.729|4.729|4.898|8.805|0.000|-0.167
key_arrow_down|4.564|4.729|4.729|4.895|8.805|0.000|-0.166
key_arrow_left|4.564|4.729|4.729|4.895|8.805|0.000|-0.166
key_arrow_right|4.564|4.729|4.729|4.894|8.805|-0.000|-0.165
icon_pos1|4.564|4.731|4.731|4.894|8.805|-0.000|-0.165
icon_ende|4.564|4.731|4.731|4.895|8.805|-0.000|-0.166
icon_bild_up|4.564|4.731|4.731|4.894|8.805|-0.000|-0.165
icon_bild_down|4.564|4.731|4.731|4.894|8.805|-0.000|-0.165
icon_einf|4.564|4.731|4.731|4.894|8.805|-0.000|-0.165
icon_numlock|4.564|4.729|4.729|4.894|8.805|-0.000|-0.165
icon_entf|4.564|4.577|4.577|4.894|8.805|0.000|-0.165
icon_numpad_entf|4.564|4.574|4.574|4.894|8.805|-0.000|-0.165
icon_pause|4.564|4.729|4.729|4.898|8.805|-0.000|-0.167
icon_pause_rose|4.564|4.729|4.729|4.894|8.805|-0.000|-0.165
icon_rollen|4.564|4.731|4.731|4.898|8.805|0.000|-0.167
icon_rollen_rose|4.564|4.729|4.729|4.894|8.805|-0.000|-0.165
icon_druck|4.564|4.729|4.729|4.898|8.805|0.000|-0.167
icon_druck_rose|4.564|4.731|4.731|4.894|8.805|0.000|-0.165
```

**Echte Ausreißer:** keine auf `topD`/`h` (alle 4.564 mm / 8.805 mm, außer den geometrisch
begründeten Sonderformen enter_iso/numpad_enter). Icons sind sauber auf einer gemeinsamen
Ankerlinie.

### Cluster 4 — Sonderstücke: 11 Novelty-Tasten

| Größe | Median | Min | Max |
|---|---|---|---|
| topD | 5.073 mm | 4.564 mm | 5.918 mm (cassette) |
| leftD | 4.731 mm | 4.729 mm | 5.897 mm (mic) |
| rightD | 4.731 mm | 4.729 mm | 5.897 mm |
| botD | 5.404 mm | 4.894 mm | 6.249 mm (cassette) |
| h | 7.786 mm | 6.096 mm (cassette) | 8.805 mm |
| dx | 0.000 mm | 0.000 mm | 0.000 mm |
| dy | −0.165 mm | −0.167 mm | −0.165 mm |

```
novelty_vinyl|4.564|4.731|4.731|4.894|8.805|-0.000|-0.165
novelty_eq|4.564|4.814|4.814|4.894|8.805|-0.000|-0.165
novelty_note|4.564|5.120|5.120|4.894|8.805|-0.000|-0.165
novelty_headphones|5.664|4.731|4.731|5.995|6.604|-0.000|-0.165
novelty_mic|4.564|5.897|5.897|4.894|8.805|-0.000|-0.165
novelty_dial|4.564|4.729|4.729|4.894|8.805|-0.000|-0.165
novelty_vol_up|5.387|4.729|4.729|5.718|7.158|-0.000|-0.165
novelty_note2|5.277|4.731|4.731|5.612|7.378|-0.000|-0.167
novelty_cassette|5.918|4.731|4.731|6.249|6.096|-0.000|-0.166
novelty_heart|5.073|4.900|4.900|5.404|7.786|-0.000|-0.165
novelty_vol_down|5.387|4.729|4.729|5.718|7.158|-0.000|-0.165
```
Alle 11 Novelty-Icons sind horizontal exakt zentriert (dx=0.000 über alle 11), vertikal einheitlich
bei dy≈−0.165/−0.167 mm — die Höhen-/Top-Streuung ist reine Icon-Bildgröße (je nach Motiv), kein
Positionsfehler. Kein echter Ausreißer.

---

## SET 2 — Alpine-133 (`templates/release/release_alpine_133_2026-09-23.af`, Commit 6afa068)

Datei war beim Start bereits in einer offenen Affinity-Instanz geladen (lock-Datei vorhanden) —
diese Instanz wurde read-only weiterverwendet, **nicht gespeichert**. Layer: `底色` (Face) /
`Alphas_Alpine` (Legenden). Familie: STA-artig (Alpine).

**Wichtiger Strukturunterschied zu Hello:** Alpine-Icons/F-Reihe/Esc sind **Dot-Matrix**
(`ContainerNode` mit `_pixels`-Suffix, viele `ShapeNode`-Punkte), nicht Vektor-Wortlegenden wie
bei Hello. Cluster-1-Hauptzeichen sind **TL-anchored** (top-left), nicht TC wie bei Hello:
`topD` UND `leftD` sind konstant, `rightD` variiert mit der Glyphbreite.

### Cluster 1 — Hauptzeichen (n=64; Buchstaben, Umlaute, Ziffern, Sonderzeichen — F-Reihe ist bei
Alpine Dot-Matrix, siehe Cluster 3)

| Größe | Median | Min | Max |
|---|---|---|---|
| topD | 3.463 mm | 2.362 mm (ue) | 3.804 mm (hash_r4) |
| leftD | 5.274 mm | 5.176 mm | 5.789 mm (numpad_sub_r1) |
| rightD | 10.128 mm | 7.627 mm | 28.793 mm (numpad_0, 2u breit) |
| botD | 10.759 mm | 10.435 mm | 31.649 mm (numpad_plus, 2u hoch) |
| h | 3.911 mm | 0.762 mm (colon/dash) | 5.140 mm (ue/oe) |
| dx | −2.421 mm | −11.760 mm (numpad_0) | −1.158 mm |
| dy | −3.648 mm | −14.093 mm (numpad_plus) | −3.486 mm |

Volltabelle:
```
key_q|3.463|5.249|8.682|10.435|4.235|-1.717|-3.486
key_w|3.463|5.310|7.627|10.759|3.911|-1.158|-3.648
key_e|3.463|5.242|10.259|10.759|3.911|-2.509|-3.648
key_r|3.463|5.282|9.895|10.759|3.911|-2.307|-3.648
key_t|3.463|5.230|9.713|10.759|3.911|-2.241|-3.648
key_z|3.463|5.305|9.939|10.759|3.911|-2.317|-3.648
key_u|3.463|5.237|9.801|10.703|3.967|-2.282|-3.620
key_i|3.463|5.277|12.213|10.759|3.911|-3.468|-3.648
key_o|3.463|5.278|8.871|10.647|4.023|-1.796|-3.592
key_p|3.463|5.295|10.089|10.759|3.911|-2.397|-3.648
key_a|3.463|5.280|9.199|10.759|3.911|-1.960|-3.648
key_s|3.463|5.256|10.133|10.647|4.023|-2.438|-3.592
key_d|3.463|5.273|9.379|10.759|3.911|-2.053|-3.648
key_f|3.463|5.228|10.379|10.759|3.911|-2.575|-3.648
key_g|3.463|5.275|8.986|10.647|4.023|-1.855|-3.592
key_h|3.463|5.266|9.738|10.759|3.911|-2.236|-3.648
key_j|3.463|5.282|10.593|10.703|3.967|-2.655|-3.620
key_k|3.463|5.238|9.694|10.759|3.911|-2.228|-3.648
key_l|3.463|5.289|10.357|10.759|3.911|-2.534|-3.648
key_y|3.463|5.289|9.335|10.759|3.911|-2.023|-3.648
key_x|3.463|5.265|9.236|10.759|3.911|-1.986|-3.648
key_c|3.463|5.281|9.415|10.647|4.023|-2.067|-3.592
key_v|3.463|5.237|9.275|10.759|3.911|-2.019|-3.648
key_b|3.463|5.284|10.022|10.759|3.911|-2.369|-3.648
key_n|3.463|5.260|9.716|10.759|3.911|-2.228|-3.648
key_m|3.463|5.291|8.987|10.759|3.911|-1.848|-3.648
key_ue|2.362|5.293|9.745|10.630|5.140|-2.226|-4.134
key_ae|2.515|5.280|9.199|10.534|5.084|-1.960|-4.009
key_oe|2.515|5.269|8.881|10.478|5.140|-1.806|-3.982
key_ss|3.463|5.301|10.099|10.536|4.134|-2.399|-3.536
key_num_1|3.463|5.274|11.446|10.759|3.911|-3.086|-3.648
key_num_2|3.463|5.285|10.194|10.703|3.967|-2.454|-3.620
key_num_3|3.463|5.322|10.151|10.703|3.967|-2.415|-3.620
key_num_4|3.463|5.332|9.767|10.759|3.911|-2.218|-3.648
key_num_5|3.463|5.261|10.146|10.703|3.967|-2.443|-3.620
key_num_6|3.463|5.290|10.078|10.703|3.967|-2.394|-3.620
key_num_7|3.463|5.330|10.183|10.759|3.911|-2.427|-3.648
key_num_8|3.463|5.268|10.216|10.642|4.028|-2.474|-3.589
key_num_9|3.463|5.245|10.123|10.703|3.967|-2.439|-3.620
key_num_0|3.463|5.261|9.670|10.647|4.023|-2.205|-3.592
key_numpad_1|3.463|5.273|11.446|10.759|3.911|-3.087|-3.648
key_numpad_2|3.463|5.273|10.206|10.703|3.967|-2.467|-3.620
key_numpad_3|3.463|5.273|10.201|10.703|3.967|-2.464|-3.620
key_numpad_4|3.463|5.273|9.826|10.759|3.911|-2.277|-3.648
key_numpad_5|3.463|5.273|10.134|10.703|3.967|-2.431|-3.620
key_numpad_6|3.463|5.273|10.094|10.703|3.967|-2.411|-3.620
key_numpad_7|3.463|5.273|10.240|10.759|3.911|-2.483|-3.648
key_numpad_8|3.463|5.273|10.212|10.642|4.028|-2.469|-3.589
key_numpad_9|3.463|5.273|10.094|10.703|3.967|-2.411|-3.620
key_numpad_0|3.463|5.273|28.793|10.647|4.023|-11.760|-3.592
key_numpad_0_r1|3.463|5.273|9.659|10.647|4.023|-2.193|-3.592
key_numpad_plus|3.463|5.273|10.766|31.649|2.095|-2.746|-14.093
key_numpad_div_r1|3.463|5.490|10.653|10.817|3.852|-2.582|-3.677
key_numpad_mul_r1|3.466|5.455|10.584|12.572|2.095|-2.564|-4.553
key_numpad_sub_r1|3.463|5.789|10.909|13.908|0.762|-2.560|-5.223
key_caret|3.463|5.270|10.997|12.804|1.866|-2.864|-4.671
key_acute|3.463|5.176|11.091|12.804|1.866|-2.958|-4.671
key_plus|3.463|5.336|10.703|12.575|2.095|-2.683|-4.556
key_semicolon|3.438|5.292|12.030|13.213|1.481|-3.369|-4.888
key_colon|3.429|5.339|12.018|13.927|0.776|-3.339|-5.249
key_dash|3.451|5.319|11.379|13.920|0.762|-3.030|-5.234
key_hash_r3|3.464|5.292|10.502|11.718|2.950|-2.605|-4.127
key_hash_r4|3.804|5.462|19.918|11.378|2.950|-7.228|-3.787
key_less_r2|3.463|5.292|10.598|12.299|2.370|-2.653|-4.418
```

**Echte Ausreißer (Ankerdimensionen topD + leftD, TL-Gruppe):**
- `key_ue` (topD 2.362 mm, −1.10 mm), `key_ae`/`key_oe` (topD 2.515 mm, −0.95 mm) — Umlaute
  systematisch höher angesetzt (Punkte über dem Buchstaben brauchen mehr Raum) — plausibel,
  aber deutlich außerhalb der 0.3-mm-Grenze, Anton sollte bestätigen, dass das gewollt ist.
- `key_hash_r4` (topD 3.804 mm, +0.34 mm; leftD 5.462 mm, +0.19 mm) — knapp über der Grenze,
  vermutlich Sondergröße der ANSI/Reserve-Raute-Taste.
- `key_numpad_sub_r1` (leftD 5.789 mm, +0.52 mm) — deutlich nach rechts versetzt, zusätzlich
  h=0.762 mm (kleinster Wert im Cluster) — sieht wie eine verkürzte/verschobene Legende aus,
  gleiches Muster wie bei Hello (`key_numpad_sub`).

### Cluster 2 — Mehrfachbelegung (Subs n=20, AltGr n=12)

**Subs:**

| Größe | Median | Min | Max |
|---|---|---|---|
| topD | 3.463 mm | 3.443 mm | 6.612 mm (dash_sub) |
| leftD | 10.869 mm | 9.926 mm | 21.341 mm (hash_r4_sub) |
| rightD | 5.300 mm | 5.143 mm | 5.370 mm |
| botD | 11.230 mm | 10.418 mm | 13.064 mm |
| h | 2.731 mm | 0.762 mm (dash_sub) | 4.252 mm |
| dxMain | 2.785 mm | 2.288 mm | 8.016 mm (hash_r4_sub) |
| dyMain | −3.888 mm | −4.800 mm | −2.073 mm (dash_sub) |
| hRatio | ~0.99 (Ziffern) | 0.399 (num_0_sub) | 3.109 (colon_sub) |

```
key_caret_sub|3.463|11.012|5.255|12.804|1.866|2.879|-4.671|dxMain=5.742|dyMain=-0.000|hRatio=1.000
key_num_1_sub|3.463|12.123|5.295|10.790|3.880|3.414|-3.664|dxMain=6.500|dyMain=-0.016|hRatio=0.992
key_num_2_sub|3.463|10.922|5.345|12.804|1.866|2.789|-4.671|dxMain=5.243|dyMain=-1.050|hRatio=0.470
key_num_3_sub|3.463|10.767|5.314|10.736|3.934|2.727|-3.636|dxMain=5.141|dyMain=-0.016|hRatio=0.992
key_num_4_sub|3.463|10.334|5.254|10.418|4.252|2.540|-3.478|dxMain=4.758|dyMain=0.170|hRatio=1.087
key_num_5_sub|3.463|9.926|5.349|10.790|3.880|2.288|-3.664|dxMain=4.731|dyMain=-0.043|hRatio=0.978
key_num_6_sub|3.463|10.049|5.227|10.790|3.880|2.411|-3.664|dxMain=4.805|dyMain=-0.043|hRatio=0.978
key_num_7_sub|3.463|10.816|5.328|10.818|3.852|2.744|-3.677|dxMain=5.170|dyMain=-0.029|hRatio=0.985
key_num_8_sub|3.463|11.358|5.370|10.594|4.076|2.994|-3.565|dxMain=5.468|dyMain=0.024|hRatio=1.012
key_num_9_sub|3.463|11.355|5.367|10.578|4.091|2.994|-3.558|dxMain=5.433|dyMain=0.062|hRatio=1.031
key_num_0_sub|3.463|10.659|5.328|13.064|1.606|2.666|-4.800|dxMain=4.870|dyMain=-1.208|hRatio=0.399
key_ss_sub|3.463|10.477|5.277|10.587|4.083|2.600|-3.562|dxMain=4.999|dyMain=-0.026|hRatio=0.988
key_acute_sub|3.463|11.105|5.162|12.804|1.866|2.972|-4.671|dxMain=5.929|dyMain=0.000|hRatio=1.005
key_plus_sub|3.463|10.800|5.238|12.575|2.095|2.781|-4.556|dxMain=5.465|dyMain=-0.000|hRatio=1.000
key_semicolon_sub|3.443|11.983|5.338|11.642|3.048|3.323|-4.100|dxMain=6.692|dyMain=0.788|hRatio=2.057
key_colon_sub|3.480|12.075|5.282|12.240|2.413|3.397|-4.380|dxMain=6.736|dyMain=0.869|hRatio=3.109
key_dash_sub|6.612|10.735|5.304|10.759|0.762|2.715|-2.073|dxMain=5.746|dyMain=3.161|hRatio=1.000
key_hash_r3_sub|3.464|11.920|5.143|12.803|1.866|3.388|-4.669|dxMain=5.994|dyMain=-0.542|hRatio=0.632
key_hash_r4_sub|3.463|21.341|5.309|12.804|1.866|8.016|-4.671|dxMain=15.244|dyMain=-0.884|hRatio=0.632
key_less_r2_sub|3.463|10.584|5.292|12.299|2.370|2.646|-4.418|dxMain=5.299|dyMain=0.000|hRatio=1.000
```

**Echter Ausreißer:** `key_dash_sub` — topD 6.612 mm statt 3.463 mm (+3.15 mm!), zugleich dyMain
+3.161 mm (Sub liegt UNTER statt über dem Hauptzeichen) und h nur 0.762 mm. Das weicht so stark
vom Rest des Clusters ab (alle anderen Subs sitzen oben rechts, topD≈3.46–3.48 mm), dass es wie
eine falsch platzierte oder falsch benannte Legende aussieht — bitte Anton/Builder gezielt prüfen.
`key_hash_r4_sub` (leftD 21.34 mm, dxMain 15.24 mm) ist ebenfalls extrem weit rechts — vermutlich
weil `key_hash_r4` selbst eine sehr breite/Sonderform-Taste ist (siehe Cluster 1).

**AltGr:**

| Größe | Median | Min | Max |
|---|---|---|---|
| topD | 9.769 mm | 9.214 mm (less_r2_gr) | 12.251 mm (plus_gr) |
| leftD | 11.386 mm | 10.076 mm | 12.195 mm |
| rightD | 5.281 mm | 5.156 mm | 5.408 mm |
| botD | 5.115 mm | 5.043 mm | 5.146 mm |
| h | 3.251 mm | 0.776 mm (plus_gr) | 3.809 mm (less_r2_gr) |
| dxMain | — (nur direkt gemessen, siehe unten) |
| dyMain | — |

```
key_num_2_gr|11.168|11.540|5.201|5.127|1.839|3.170|3.020|dxMain=5.624|dyMain=6.641|hRatio=0.464
key_num_3_gr|11.184|11.585|5.156|5.110|1.839|3.215|3.037|dxMain=5.629|dyMain=6.658|hRatio=0.464
key_num_7_gr|9.533|11.389|5.332|5.146|3.454|3.029|2.194|dxMain=5.455|dyMain=5.842|hRatio=0.883
key_num_8_gr|9.550|11.431|5.291|5.129|3.454|3.070|2.211|dxMain=5.543|dyMain=5.800|hRatio=0.857
key_num_9_gr|9.559|11.384|5.338|5.120|3.454|3.023|2.219|dxMain=5.462|dyMain=5.840|hRatio=0.871
key_num_0_gr|9.559|11.417|5.305|5.120|3.454|3.056|2.219|dxMain=5.261|dyMain=5.812|hRatio=0.859
key_ss_gr|9.550|11.107|5.262|5.126|3.457|2.923|2.212|dxMain=5.322|dyMain=5.749|hRatio=0.836
key_plus_gr|12.251|10.957|5.271|5.105|0.776|2.843|3.573|dxMain=5.527|dyMain=8.129|hRatio=0.370
key_m_gr|10.253|11.061|5.302|5.043|2.836|2.879|2.605|dxMain=4.727|dyMain=6.253|hRatio=0.725
key_q_gr|10.233|10.098|5.271|5.105|2.794|2.413|2.564|dxMain=4.130|dyMain=6.050|hRatio=0.660
key_e_gr|9.979|10.076|5.271|5.105|3.048|2.403|2.437|dxMain=4.912|dyMain=6.085|hRatio=0.779
key_less_r2_gr|9.214|12.195|5.408|5.110|3.809|3.394|2.052|dxMain=6.047|dyMain=6.470|hRatio=0.660
```

**AltGr-Höhe in pt — Widerspruch zur Note "16,94 pt" geprüft:**
Gemessene AltGr-Legendenhöhe (mm): Median **3.251 mm** (min 0.776 mm bei `plus_gr` [Zeichen "="
flach], max 3.809 mm bei `less_r2_gr`). Umrechnung mm→pt (1 pt = 0.352778 mm): Median ≈
**9.22 pt**, Bereich ≈ 2.2–10.8 pt. Der Notenwert 16,94 pt entspräche 5.976 mm Cap-Höhe — das
ist **fast doppelt so groß** wie der gemessene Median und liegt sogar über dem größten gemessenen
Einzelwert. **Bestätigt: der Notenwert 16,94 pt passt nicht zur gemessenen Alpine-Geometrie** —
er wurde vermutlich vom Hello-Set übernommen (Hello-AltGr-Median 3.308 mm ≈ 9.38 pt liegt näher
dran, aber auch nicht bei 16,94 pt). Wahrscheinlicher: 16,94 pt war die am Text-Tool eingestellte
**Punktgröße vor Konvertierung zu Kurven** (Font-Ascent/Cap-Height-Verhältnis macht die gemessene
Bbox-Höhe kleiner als die Punktgröße) — das kann ohne Kenntnis des genauen Fonts nicht aus der
Bbox zurückgerechnet werden. Für die Druckanweisung sollte der **gemessene mm-Wert (3.25 mm
Median)**, nicht der Notenwert, verwendet werden.

### Cluster 3 — Icons (n=61: Modifier, Nav, Pfeile, Enter/Tab/Caps/Backspace + F-Reihe als
Dot-Matrix `_pixels`)

Anker: topD **konstant exakt 3.632 mm über alle 61 Icons** (keine Streuung, Min=Max). Höhe zwei
Klassen: F-Reihe **3.648 mm** (dünneres Dot-Matrix-Panel) vs. alle übrigen Icons **7.500 mm**
(Pfeile 7.449 mm, minimal kleiner).

| Größe | Median | Min | Max |
|---|---|---|---|
| topD | 3.632 mm | 3.632 mm | 3.632 mm |
| leftD | 5.334 mm | 4.922 mm | 21.790 mm (shift_r) |
| rightD | 5.334 mm | 4.922 mm | 26.759 mm (shift_l) |
| botD | 7.001 mm | 7.000 mm | 26.344 mm (ISO-Enter-Ring) |
| h | 7.500 mm | 3.648 mm (F-Reihe) | 7.500 mm |
| dx | 0.000 mm | −9.462 mm (shift_l) | 0.004 mm |
| dy | −1.684 mm | −11.356 mm (ISO-Enter) | −1.684 mm |

```
key_esc_pixels|3.632|5.309|5.309|7.001|7.500|0.000|-1.684
key_f1_pixels|3.632|6.467|6.467|10.853|3.648|-0.000|-3.610
key_f2_pixels|3.632|6.467|6.467|10.853|3.648|-0.000|-3.610
key_f3_pixels|3.632|6.467|6.467|10.853|3.648|-0.000|-3.610
key_f4_pixels|3.632|6.467|6.467|10.853|3.648|-0.000|-3.610
key_f5_pixels|3.632|6.467|6.467|10.853|3.648|-0.000|-3.610
key_f6_pixels|3.632|6.467|6.467|10.853|3.648|-0.000|-3.610
key_f7_pixels|3.632|6.467|6.467|10.853|3.648|-0.000|-3.610
key_f8_pixels|3.632|6.467|6.467|10.853|3.648|-0.000|-3.610
key_f9_pixels|3.632|6.467|6.467|10.853|3.648|-0.000|-3.610
key_f10_pixels|3.632|4.922|4.922|10.853|3.648|-0.000|-3.610
key_f11_pixels|3.632|4.922|4.922|10.853|3.648|-0.000|-3.610
key_f12_pixels|3.632|4.922|4.922|10.853|3.648|-0.000|-3.610
key_ctrl_l_pixels|3.632|7.514|7.506|7.001|7.500|0.004|-1.684
key_ctrl_r_pixels|3.632|7.510|7.510|7.001|7.500|-0.000|-1.684
key_strg_r1_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_alt_pixels|3.632|7.510|7.510|7.001|7.500|-0.000|-1.684
key_alt_r1_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_altgr_pixels|3.632|7.510|7.510|7.001|7.500|-0.000|-1.684
key_win_pixels|3.632|7.510|7.510|7.001|7.500|0.000|-1.684
key_win_r_pixels|3.632|7.510|7.510|7.001|7.500|-0.000|-1.684
key_menu_pixels|3.632|7.510|7.510|7.001|7.500|-0.000|-1.684
key_menu_r1_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_fn_r1_pixels|3.632|5.309|5.309|7.001|7.500|0.000|-1.684
key_shift_l_pixels|3.632|7.835|26.759|7.001|7.500|-9.462|-1.684
key_shift_r_pixels|3.632|21.790|21.790|7.001|7.500|-0.000|-1.684
key_1u_shift_r2_pixels|3.632|5.309|5.309|7.000|7.500|-0.000|-1.684
key_1.25u_shift_r2_pixels|3.632|7.510|7.510|7.001|7.500|-0.000|-1.684
key_1.75u_shift_r2_pixels|3.632|12.564|12.564|7.000|7.500|-0.000|-1.684
key_2u_shift_r2_pixels|3.632|14.875|14.876|7.000|7.500|-0.000|-1.684
key_caps_pixels|3.632|7.943|17.184|7.001|7.500|-4.620|-1.684
key_tab_pixels|3.632|8.096|12.108|7.001|7.500|-2.006|-1.684
key_backspace_pixels|3.632|14.876|14.875|7.001|7.500|0.000|-1.684
key_enter_pixels|3.632|17.297|17.297|7.001|7.500|0.000|-1.684
key_ISO_Enter_r3_pixels|3.632|10.295|10.295|26.344|7.500|-0.000|-11.356
key_numpad_enter_pixels|3.632|5.309|5.309|26.075|7.500|0.000|-11.221
key_pos1_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_ende_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_ende_r2_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_ende_r3_pixels|3.632|5.309|5.309|7.001|7.500|0.000|-1.684
key_bild_up_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_bild_up_r3_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_bild_up_r4_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_bild_down_pixels|3.632|5.309|5.309|7.001|7.500|0.000|-1.684
key_bild_down_r2_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_bild_down_r3_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_einf_pixels|3.632|5.309|5.309|7.001|7.500|0.000|-1.684
key_einf_r1_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_entf_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_entf_r1_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_entf_r2_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_entf_r3_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_numpad_entf_r1_pixels|3.632|5.309|5.309|7.001|7.500|0.000|-1.684
key_numlock_pixels|3.632|5.309|5.309|7.001|7.500|-0.000|-1.684
key_druck_pixels|3.632|5.309|5.309|7.001|7.500|0.000|-1.684
key_rollen_pixels|3.632|6.081|6.081|7.001|7.500|-0.000|-1.684
key_pause_pixels|3.632|6.853|6.853|7.001|7.500|-0.000|-1.684
key_arrow_up_pixels|3.632|5.334|5.334|7.052|7.449|-0.000|-1.710
key_arrow_down_pixels|3.632|5.334|5.334|7.052|7.449|-0.000|-1.710
key_arrow_left_pixels|3.632|5.334|5.334|7.052|7.449|-0.000|-1.710
key_arrow_right_pixels|3.632|5.334|5.334|7.052|7.449|-0.000|-1.710
```

**Echte Ausreißer:** keine auf `topD` (exakt konstant). Die F-Reihe hat eine SYSTEMATISCH andere
Höhe (3.648 mm statt 7.500 mm — Faktor 0.49×) als alle anderen Icons; das ist eine bewusste
Design-Klasse (dünneres F-Zeilen-Panel), kein Zufallsausreißer, aber sollte in der Druckanweisung
als eigene Zeile geführt werden, nicht mit den übrigen Icons gemittelt.

### Cluster 4 — Sonderstücke (Alpine)

| Stück | Gefunden als | topD | leftD | rightD | botD | h | dx | dy |
|---|---|---|---|---|---|---|---|---|
| EmbeddedDoc "Esc" | **Korrektur:** `key_esc_pixels` ist in dieser Release-Datei ein Dot-Matrix-Panel (68 Punkte, `ContainerNode`), **keine** `EmbeddedDocumentNode` — siehe Cluster 3 für seine Werte (topD 3.632, h 7.500 mm). Eine echte `EmbeddedDocumentNode` mit Esc-Bezug wurde nicht gefunden. |
| `key_empty` Icon | `key_empty_icon` (EmbeddedDocumentNode, Layer `Images`, geclippt auf `key_empty_face`) | 2.132 mm | 3.898 mm | 3.904 mm | 5.670 mm | 10.332 mm | −0.003 mm | −1.768 mm |
| Enter-Ring | `key_ISO_Enter_r3_pixels` (=Cluster-3-Wert) | 3.632 mm | 10.295 mm | 10.295 mm | 26.344 mm | 7.500 mm | −0.000 mm | −11.356 mm |
| Spacebar Dot-Matrix | `key_space_pixels` vs. `key_space_face` | 3.632 mm | 5.623 mm | 5.623 mm | 6.089 mm | 8.412 mm | 0.000 mm | −1.228 mm |
| Homing-Bars F/J | **NICHT GEPRÜFT** — kein Node mit Namen wie `*bar*`/`*homing*`/`*nub*` gefunden; `key_f_face`/`key_j_face` haben keine Kind-Nodes. Wahrscheinlich Teil der Layer `键帽` (3D-Keycap-Kunstwerk, 4 GroupNodes `keycap_art_1..4`, nicht einzeln benannt) oder physisch am realen Cap (nicht im Vektor-Template abgebildet). Ohne eindeutigen Node kann keine Legendenposition gemessen werden. |

`key_empty_icon`-Face-Box zur Nachvollziehbarkeit (px, 300 dpi): Face x=5422.56 y=678.49
w=214.17 h=214.17; Icon x=5468.59 y=703.67 w=122.03 h=122.03.

---

## Zusammenfassung Kurzfassung (siehe Antworttext) und Auffälligkeiten für Anton siehe Antworttext.

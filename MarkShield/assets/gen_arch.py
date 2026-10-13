"""
Generate a clean, professional MarkShield system architecture diagram.
Final polished version – no text overlaps, clear flow.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

fig, ax = plt.subplots(figsize=(24, 16))
ax.set_xlim(0, 24)
ax.set_ylim(0, 16)
ax.axis('off')
fig.patch.set_facecolor('#F5F7FA')

# ── Palette ───────────────────────────────────────────────────────────────
C_INPUT  = ('#E8F5E9', '#2E7D32', '#1B5E20')
C_DWT    = ('#E3F2FD', '#1565C0', '#0D47A1')
C_SVD    = ('#FFF3E0', '#E65100', '#BF360C')
C_LOGO   = ('#FCE4EC', '#C2185B', '#880E4F')
C_CRYPTO = ('#F3E5F5', '#6A1B9A', '#4A148C')
C_LSB    = ('#E1F5FE', '#0277BD', '#01579B')
C_OUT    = ('#E8F5E9', '#2E7D32', '#1B5E20')
C_VER    = ('#FFF8E1', '#F57F17', '#BF360C')
C_SEC    = ('#FBE9E7', '#BF360C', '#880E4F')
C_KEY    = ('#ECEFF1', '#455A64', '#263238')


def box(ax, x, y, w, h, colors, title, lines,
        title_sz=10, body_sz=8.8):
    bg, border, tc = colors
    r = FancyBboxPatch((x, y), w, h,
                       boxstyle='round,pad=0.08',
                       facecolor=bg, edgecolor=border,
                       linewidth=2.0, zorder=3)
    ax.add_patch(r)
    sep_y = y + h - 0.58
    ax.plot([x+0.1, x+w-0.1], [sep_y, sep_y],
            color=border, lw=0.9, alpha=0.4, zorder=4)
    ax.text(x+w/2, y+h-0.30, title,
            ha='center', va='top', fontsize=title_sz,
            fontweight='bold', color=tc, zorder=4)
    gap = (sep_y - y - 0.08) / max(len(lines), 1)
    for i, ln in enumerate(lines):
        ax.text(x+w/2, sep_y - 0.04 - gap*(i+0.5),
                ln, ha='center', va='center',
                fontsize=body_sz, color='#263238', zorder=4)


def ah(ax, x1, y, x2, c='#37474F', lbl=''):
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='-|>', color=c,
                                lw=1.7, mutation_scale=13), zorder=5)
    if lbl:
        ax.text((x1+x2)/2, y+0.12, lbl,
                ha='center', va='bottom', fontsize=7.5,
                color=c, style='italic', zorder=6)


def av(ax, x, y1, y2, c='#37474F', lbl='', lr=True):
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='-|>', color=c,
                                lw=1.7, mutation_scale=13), zorder=5)
    if lbl:
        dx = 0.12 if lr else -0.12
        ax.text(x+dx, (y1+y2)/2, lbl,
                ha='left' if lr else 'right', va='center',
                fontsize=7.5, color=c, style='italic', zorder=6)


def elbow_rd(ax, x1, y1, x2, y2, c='#37474F', lbl=''):
    """Right then down elbow."""
    ax.plot([x1, x2], [y1, y1], color=c, lw=1.7, zorder=5)
    ax.annotate('', xy=(x2, y2), xytext=(x2, y1),
                arrowprops=dict(arrowstyle='-|>', color=c,
                                lw=1.7, mutation_scale=13), zorder=5)
    if lbl:
        ax.text(x2+0.1, (y1+y2)/2, lbl,
                ha='left', va='center', fontsize=7.5,
                color=c, style='italic', zorder=6)


def elbow_dl(ax, x1, y1, x2, y2, c='#37474F', lbl=''):
    """Down then left elbow."""
    ax.plot([x1, x1], [y1, y2], color=c, lw=1.7, zorder=5)
    ax.annotate('', xy=(x2, y2), xytext=(x1, y2),
                arrowprops=dict(arrowstyle='-|>', color=c,
                                lw=1.7, mutation_scale=13), zorder=5)
    if lbl:
        ax.text(x1+0.1, (y1+y2)/2, lbl,
                ha='left', va='center', fontsize=7.5,
                color=c, style='italic', zorder=6)


def section_bg(ax, x, y, w, h, c, lbl):
    r = FancyBboxPatch((x, y), w, h,
                       boxstyle='round,pad=0.1',
                       facecolor=c, edgecolor=c,
                       alpha=0.10, linewidth=1.5, zorder=1)
    ax.add_patch(r)
    ax.text(x+0.3, y+0.22, lbl,
            ha='left', va='bottom', fontsize=8.5,
            fontweight='bold', color=c, alpha=0.65, zorder=2)


# ══════════════════════════════════════════════════════════════════
#  TITLE
# ══════════════════════════════════════════════════════════════════
ax.text(12, 15.65,
        'MarkShield  —  Dual-Layer Hybrid Digital Protection Architecture',
        ha='center', va='top', fontsize=17, fontweight='bold',
        color='#1A237E')

# ══════════════════════════════════════════════════════════════════
#  SECTION BACKGROUNDS
# ══════════════════════════════════════════════════════════════════
section_bg(ax, 0.3, 9.3, 23.4, 5.9,
           '#1565C0', 'LAYER 1 — DWT-SVD FREQUENCY-DOMAIN WATERMARKING')
section_bg(ax, 0.3, 4.3, 23.4, 4.7,
           '#6A1B9A', 'LAYER 2 — AES-256 ENCRYPTED SPATIAL-DOMAIN STEGANOGRAPHY')
section_bg(ax, 0.3, 0.4, 23.4, 3.6,
           '#E65100', 'VERIFICATION & EXTRACTION PIPELINE')

# ══════════════════════════════════════════════════════════════════
#  ROW 1  –  Watermarking  (y_base=9.75, height=4.8)
# ══════════════════════════════════════════════════════════════════
BW, BH, BY = 3.8, 4.2, 9.75

box(ax, 0.5,  BY, BW, BH, C_INPUT,
    '1   Input Layer',
    ['RGB Cover Image (512×512×3)',
     'Convert to YCrCb colour space',
     'Isolate Luminance channel Y',
     'Keep Cr, Cb channels intact'])

box(ax, 4.8,  BY, BW, BH, C_DWT,
    '2   2D Haar DWT',
    ['Apply Haar wavelet ψ to Y',
     'Decompose → 4 subbands:',
     '    LL   LH   HL   HH',
     'Target: HL subband for embed'])

box(ax, 9.1,  BY, BW, BH, C_SVD,
    '3   SVD Embedding',
    ['SVD on HL:  U_A · S_A · V_Aᵀ',
     'M = diag(S_A) + α · Logo_norm',
     'SVD(M) → U_M · S_M · V_Mᵀ',
     'HL_wm = U_A · diag(S_M) · V_Aᵀ'])

box(ax, 13.4, BY, BW, BH, C_DWT,
    '4   IDWT Reconstruct',
    ['Restore HL with HL_wm',
     'Apply inverse 2D Haar DWT',
     'Clip float → uint8 [0, 255]',
     'Merge YCrCb → RGB image'])

box(ax, 17.7, BY, 5.9, BH, C_KEY,
    '5   Watermark Key  (.key)',
    ['Serialised Base64 JSON file:',
     '• Matrices: U_M,  V_Mᵀ,  S_A',
     '• Params: α,  wavelet,  band',
     'Eliminates SVD false-positives',
     'Required for logo extraction'])

# Logo box (above SVD)
box(ax, 10.2, 14.3, 3.2, 1.1, C_LOGO,
    '  Logo Asset',
    ['Copyright Logo (128×128 Greyscale)'],
    title_sz=9, body_sz=8.5)

# ── Row-1 arrows ──────────────────────────────────────────────
ah(ax, 0.5+BW, BY+BH/2, 4.8,  lbl='Y channel')
ah(ax, 4.8+BW, BY+BH/2, 9.1,  lbl='HL subband')
ah(ax, 9.1+BW, BY+BH/2, 13.4, lbl='HL_wm')
ah(ax, 13.4+BW, BY+BH/2, 17.7, c=C_KEY[1], lbl='wm_key')

# Logo to SVD block: down then left
ax.plot([11.8, 11.8], [14.3, BY+BH*0.65], color=C_LOGO[1], lw=1.7, zorder=5)
ax.annotate('', xy=(9.1+BW, BY+BH*0.65), xytext=(11.8, BY+BH*0.65),
            arrowprops=dict(arrowstyle='-|>', color=C_LOGO[1],
                            lw=1.7, mutation_scale=13), zorder=5)
ax.text(10.7, BY+BH*0.65+0.1, 'Logo_norm', ha='center', va='bottom',
        fontsize=7.5, color=C_LOGO[1], style='italic', zorder=6)

# Watermarked image goes DOWN to row 2 (via right side of IDWT)
av(ax, 15.3, BY, 8.5+0.1, c=C_DWT[1], lbl='I_wm', lr=True)

# ══════════════════════════════════════════════════════════════════
#  ROW 2  –  Steganography  (y_base=4.65, height=3.5)
# ══════════════════════════════════════════════════════════════════
SW, SH, SY = 3.8, 3.3, 4.75

box(ax, 0.5,  SY, SW, SH, C_SEC,
    '6   Secret Input',
    ['Secret Text Payload (UTF-8)',
     'User Master Password',
     '(any length or complexity)'])

box(ax, 4.8,  SY, SW, SH, C_CRYPTO,
    '7   Crypto Engine',
    ['PBKDF2HMAC-SHA256  (100k iter)',
     '→ 256-bit AES key',
     'AES-256-CBC Encrypt + PKCS7',
     'Random Salt (16B) + IV (16B)'])

box(ax, 9.1,  SY, SW, SH, C_CRYPTO,
    '8   Packet Formatter',
    ['MAGIC header: "MSST" (4 B)',
     'Payload length field (4 B)',
     'Append ciphertext bytes',
     'Validate LSB image capacity'])

box(ax, 13.4, SY, SW, SH, C_LSB,
    '9   LSB Embedder',
    ['For each bit b_k in stream:',
     'I*[k] = (I_wm[k] & 0xFE) | b_k',
     'Changes only LSB → ±1 pixel',
     'PSNR > 42 dB  ·  SSIM > 0.99'])

box(ax, 17.7, SY, 5.9, SH, C_OUT,
    '10  Protected Output',
    ['MarkShield Image I*  (.png)',
     'Watermark Key file  (.key)',
     'Dual-layer protection active',
     'Ready for distribution'])

# ── Row-2 arrows ──────────────────────────────────────────────
ah(ax, 0.5+SW, SY+SH/2, 4.8,   lbl='text + pwd')
ah(ax, 4.8+SW, SY+SH/2, 9.1,   lbl='enc. packet')
ah(ax, 9.1+SW, SY+SH/2, 13.4,  lbl='bitstream')
ah(ax, 13.4+SW, SY+SH/2, 17.7, c=C_OUT[1], lbl='I* protected')

# I_wm from IDWT meets LSB Embedder top
ax.annotate('', xy=(15.3, SY+SH), xytext=(15.3, BY),
            arrowprops=dict(arrowstyle='-|>', color=C_DWT[1],
                            lw=1.7, mutation_scale=13), zorder=5)
ax.text(15.4, (BY + SY+SH)/2, 'I_wm', ha='left', va='center',
        fontsize=7.5, color=C_DWT[1], style='italic', zorder=6)

# ══════════════════════════════════════════════════════════════════
#  ROW 3  –  Verification  (y_base=0.65, height=3.0)
# ══════════════════════════════════════════════════════════════════
VW, VH, VY = 5.2, 3.1, 0.65

box(ax, 0.5,  VY, VW, VH, C_VER,
    '11  LSB Extraction',
    ['Read flat pixel array LSBs',
     'Reconstruct byte stream',
     'Validate MAGIC header "MSST"',
     'Unpack encrypted packet bytes'])

box(ax, 6.1,  VY, VW, VH, C_VER,
    '12  AES-256 Decryption',
    ['Re-derive key: PBKDF2 + Salt',
     'AES-256-CBC Decrypt + IV',
     'PKCS7 unpad → UTF-8 plaintext',
     'BER = 0.00 on lossless image'])

box(ax, 11.7, VY, VW, VH, C_VER,
    '13  DWT-SVD Logo Extraction',
    ['2D DWT on tested/attacked image',
     'SVD on HL*: extract S_Y',
     'W_ext = (U_M · S_Y · V_Mᵀ − S_A) / α',
     'Resize → original logo resolution'])

box(ax, 17.3, VY, 6.3, VH, C_INPUT,
    '14  Quality Metrics Output',
    ['PSNR (dB)  ·  SSIM  ·  NC  ·  BER',
     'No Attack:  PSNR=48.75  NC=0.974  BER=0.00',
     'JPEG Q=40:  NC=0.962  (logo survives attacks)',
     'Tamper seal: BER > 0 → payload corrupted'])

# ── Row-3 horizontal arrows ───────────────────────────────────
ah(ax, 0.5+VW, VY+VH/2, 6.1)
ah(ax, 6.1+VW, VY+VH/2, 11.7)
ah(ax, 11.7+VW, VY+VH/2, 17.3)

# Protected output → down-right → left into LSB Extraction
#   (elbow: right side of Protected Output box, goes down then left)
px = 17.7 + 5.9   # right edge of out box
elbow_dl(ax, px-0.5, SY, VY+VH/2, 0.5+VW,
         c='#37474F', lbl='I* / attacked')

# wm_key from Key box → down → into DWT-SVD extraction
kx = 17.7 + 5.9*0.5   # centre of key box
ax.plot([kx, kx], [BY, VY+VH*0.7], color=C_KEY[1],
        lw=1.6, linestyle='--', zorder=5)
ax.annotate('', xy=(11.7+VW*0.5, VY+VH*0.7),
            xytext=(kx, VY+VH*0.7),
            arrowprops=dict(arrowstyle='-|>', color=C_KEY[1],
                            lw=1.6, mutation_scale=12), zorder=5)
ax.text(kx+0.15, (BY+VY+VH*0.7)/2, 'wm_key',
        ha='left', va='center', fontsize=7.5,
        color=C_KEY[1], style='italic', zorder=6)

# ══════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════
ax.text(12, 0.12,
        'Layer 1 (DWT-SVD): Robust frequency-domain copyright watermarking  |  '
        'Layer 2 (AES-256 LSB): Encrypted covert payload embedding  |  '
        'Sequential pipeline prevents mutual layer interference',
        ha='center', va='bottom', fontsize=8.5,
        color='#546E7A', style='italic')

plt.tight_layout(pad=0.3)
plt.savefig('d:/DWP/MarkShield/assets/fig_architecture.png',
            dpi=180, bbox_inches='tight',
            facecolor='#F5F7FA', edgecolor='none')
print("Architecture diagram saved successfully.")
plt.close()

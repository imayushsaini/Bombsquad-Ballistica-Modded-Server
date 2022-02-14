# ported from ankit scripts 
# need to update in future with easy to add custom list and more deep analysis .
# working on other features rn, will update this later , for now lets use this
import re

PATTERN = (
    r"fu+c+k|"
    r"fu+c+($|)|"
    r"fu+k+($|)|"
    r"\w*ph+u*c+k\w*\b|"
    r"\b\w+ch+o+d|"
    r"randi+|"
    r"chu+t\w*\b|"
    r"chh+a+k+[ae]|"
    r"hijd\w|"
    r"lund\b|"
    r"\bass\b|"
    r"asshole|"
    r"bi*tch|"
    r"cock|"
    r"\bga+nd\b|"
    r"ga+ndu|"
    r"tharki|"
    r"tatti|"
    r"lod\w\b|"
    r"jha+nt|"
    r"pu+s+y|"
    r"pu+z+y|"
    r"di+c+k|"
    r"\b([mb]+c+)+\b|"
    r"\b[mb]+[^a-zA-Z]?c+\b|"
    r"f.u.c.k|"
    r"b\w*s\w?d\w?k|"
    r"m.{0,4}d.?a.{0,8}c.?h.?o.?d|"
    r"b.+n.?c.?h.?o.?d|"
    r"cunt|"
    r"my+r+e|"
    r"th+y+r|"
    r"th+y+i+r|"
    r"th+aa+y+o+l+i|"
    r"th+a+y+o+l+i|"
    r"ku+nn+a+n|"
    r"na+y+i+n+t+e|"
    r"pu+ll+u|"
    r"la+(u|v)+d+\w\b|"
    r"chu+d\w*\b|"
    "sex+($|)|"
    r"bo+b(s|z)|"
    r"po+r+n|"
    r"ni+p+le+"
)

def censor(message):
    censored_message = re.sub(
        PATTERN,
        lambda match: "*" * len(match.group()),
        message,
        flags=re.IGNORECASE
    )
    return censored_message
# utils/latex_templates.py

TEMPLATES = {}

# -----------------------------------------------------------------------------
# 1. VIT ACADEMIC RISK (Devika J Nair style, Code no 1)
# -----------------------------------------------------------------------------
TEMPLATES["VIT Academic Risk"] = r"""\documentclass[10pt,article]{article}

%================ PACKAGES ==================
\usepackage[letterpaper,margin=0.35in]{geometry}
\usepackage{booktabs}
\usepackage{url}
\usepackage{enumitem}
\usepackage{tabularx}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{mathpazo}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{microtype}

\hypersetup{
colorlinks=true,
urlcolor=blue
}

\definecolor{mygrey}{gray}{0.85}

\pagestyle{empty}
\setlength{\tabcolsep}{0in}
\renewcommand{\arraystretch}{0.95}
\setlength{\parindent}{0pt}

\setlist[itemize]{
leftmargin=1.3em,
itemsep=0pt,
topsep=1pt,
parsep=0pt,
partopsep=0pt
}

\newcommand{\resheading}[1]{
\vspace{0.08cm}
{\colorbox{mygrey}{
\parbox{\dimexpr\linewidth-2\fboxsep}{
\centering \textbf{#1}
}}}
\vspace{0.04cm}
}

\newcommand{\ressubheading}[4]{
\begin{tabular*}{\textwidth}{l @{\extracolsep{\fill}} r}
\textbf{#1} & #2\\
\textit{#3} & \textit{#4}
\end{tabular*}
}

\begin{document}

%================ HEADER ==================

\begin{center}

{\fontsize{22}{24}\selectfont \textbf{\VAR{name}}}\\[-2pt]

\VAR{phone} \quad | \quad
\href{mailto:\VAR{email}}{\VAR{email}}
\BLOCK{ if linkedin } \quad | \quad \href{\VAR{linkedin}}{LinkedIn} \BLOCK{ endif }
\BLOCK{ if github } \quad | \quad \href{\VAR{github}}{GitHub} \BLOCK{ endif }
\BLOCK{ if website } \quad | \quad \href{\VAR{website}}{Website} \BLOCK{ endif }

\end{center}

\vspace{-0.25cm}


%================ SUMMARY ==================
\BLOCK{ if summary }
\resheading{PROFESSIONAL SUMMARY}
\small
\VAR{summary}
\normalsize
\BLOCK{ endif }


%================ EDUCATION ==================
\BLOCK{ if education }
\resheading{EDUCATION}
\begin{tabular}{p{0.60\linewidth} p{0.22\linewidth} p{0.12\linewidth}}
\toprule
\textbf{Course/Degree} & \textbf{Year/Dates} & \textbf{CGPA/Info}\\
\midrule
\BLOCK{ for edu in education }
\VAR{edu.degree} -- \VAR{edu.institution} & \VAR{edu.dates} & \VAR{edu.gpa if ('gpa' in edu and edu.gpa) else (edu.location if 'location' in edu else '')} \\
\BLOCK{ endfor }
\bottomrule
\end{tabular}
\BLOCK{ endif }


%================ EXPERIENCE ==================
\BLOCK{ if experience }
\resheading{PROFESSIONAL EXPERIENCE}
\BLOCK{ for exp in experience }
\ressubheading
{\VAR{exp.role}}
{\VAR{exp.dates}}
{\VAR{exp.company}}
{\VAR{exp.location if 'location' in exp else ''}}

\BLOCK{ if exp.bullet_points }
\begin{itemize}
\BLOCK{ for pt in exp.bullet_points }
\item \VAR{pt}
\BLOCK{ endfor }
\end{itemize}
\BLOCK{ endif }
\vspace{0.08cm}
\BLOCK{ endfor }
\BLOCK{ endif }


%================ TECHNICAL SKILLS ==================
\BLOCK{ if skills }
\resheading{TECHNICAL SKILLS}
\begin{itemize}
\BLOCK{ for cat, list in skills.items() }
\item \textbf{\VAR{cat}:} \VAR{list | join(', ')}
\BLOCK{ endfor }
\end{itemize}
\BLOCK{ endif }


%================ PROJECTS ==================
\BLOCK{ if projects }
\resheading{PROJECTS}
\BLOCK{ for proj in projects }
\ressubheading
{\VAR{proj.name}}
{\VAR{proj.dates if 'dates' in proj else ''}}
{\VAR{proj.technologies if 'technologies' in proj else ''}}
{}

\BLOCK{ if proj.bullet_points }
\begin{itemize}
\BLOCK{ for pt in proj.bullet_points }
\item \VAR{pt}
\BLOCK{ endfor }
\end{itemize}
\BLOCK{ endif }
\vspace{0.08cm}
\BLOCK{ endfor }
\BLOCK{ endif }


%================ CERTIFICATIONS ==================
\BLOCK{ if certifications }
\resheading{CERTIFICATIONS}
\begin{itemize}
\BLOCK{ for cert in certifications }
\item \VAR{cert.title} \BLOCK{ if cert.issuer }-- \VAR{cert.issuer}\BLOCK{ endif } \BLOCK{ if cert.date }(\VAR{cert.date})\BLOCK{ endif }
\BLOCK{ endfor }
\end{itemize}
\BLOCK{ endif }

\end{document}
"""

# -----------------------------------------------------------------------------
# 2. CLASSIC LINES (Anubhav Singh / xprilion style, Code no 2)
# -----------------------------------------------------------------------------
TEMPLATES["Classic Lines (xprilion)"] = r"""\documentclass[a4paper,20pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[pdftex]{hyperref}
\usepackage{fancyhdr}

\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.530in}
\addtolength{\evensidemargin}{-0.375in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.45in}
\addtolength{\textheight}{1in}

\urlstyle{rm}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-10pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-6pt}]

%-------------------------
% Custom commands
\newcommand{\resumeItem}[2]{
  \item\small{
    \textbf{#1}{: #2 \vspace{-2pt}}
  }
}

\newcommand{\resumeItemSingle}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-1pt}\item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{#3} & \textit{#4} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeSubItem}[2]{\resumeItem{#1}{#2}\vspace{-3pt}}

\renewcommand{\labelitemii}{$\circ$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=*]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-----------------------------
% % % % % %  CV STARTS HERE  % % % % % %

\begin{document}

%----------HEADING-----------------
\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
  \textbf{{\LARGE \VAR{name}}} & Email: \href{mailto:\VAR{email}}{\VAR{email}}\\
  \BLOCK{ if website } \href{\VAR{website}}{Website: \VAR{website}} \BLOCK{ endif } & Mobile: \VAR{phone} \\
  \BLOCK{ if linkedin } \href{\VAR{linkedin}}{LinkedIn: \VAR{linkedin}} \BLOCK{ endif } & \BLOCK{ if github } \href{\VAR{github}}{GitHub: \VAR{github}} \BLOCK{ endif } \\
\end{tabular*}

%-----------SUMMARY-----------------
\BLOCK{ if summary }
\section{Summary}
\small{\VAR{summary}}
\BLOCK{ endif }

%-----------EDUCATION-----------------
\BLOCK{ if education }
\section{Education}
  \resumeSubHeadingListStart
    \BLOCK{ for edu in education }
    \resumeSubheading
      {\VAR{edu.institution}}{\VAR{edu.location if 'location' in edu else ''}}
      {\VAR{edu.degree}}{\VAR{edu.dates}}
    \BLOCK{ endfor }
  \resumeSubHeadingListEnd
\BLOCK{ endif }
	    
%-----------SKILLS-----------------
\BLOCK{ if skills }
\section{Skills Summary}
  \resumeSubHeadingListStart
    \BLOCK{ for cat, list in skills.items() }
    \resumeSubItem{\VAR{cat}}{\VAR{list | join(', ')}}
    \BLOCK{ endfor }
  \resumeSubHeadingListEnd
\BLOCK{ endif }

%-----------EXPERIENCE-----------------
\BLOCK{ if experience }
\section{Experience}
  \resumeSubHeadingListStart
    \BLOCK{ for exp in experience }
    \resumeSubheading
      {\VAR{exp.company}}{\VAR{exp.location if 'location' in exp else ''}}
      {\VAR{exp.role}}{\VAR{exp.dates}}
      \BLOCK{ if exp.bullet_points }
      \resumeItemListStart
        \BLOCK{ for pt in exp.bullet_points }
        \resumeItemSingle{\VAR{pt}}
        \BLOCK{ endfor }
      \resumeItemListEnd
      \BLOCK{ endif }
    \BLOCK{ endfor }
  \resumeSubHeadingListEnd
\BLOCK{ endif }

%-----------PROJECTS-----------------
\BLOCK{ if projects }
\section{Projects}
  \resumeSubHeadingListStart
    \BLOCK{ for proj in projects }
    \resumeSubheading
      {\VAR{proj.name}}{\VAR{proj.dates if 'dates' in proj else ''}}
      {\VAR{proj.technologies if 'technologies' in proj else ''}}{}
      \BLOCK{ if proj.bullet_points }
      \resumeItemListStart
        \BLOCK{ for pt in proj.bullet_points }
        \resumeItemSingle{\VAR{pt}}
        \BLOCK{ endfor }
      \resumeItemListEnd
      \BLOCK{ endif }
    \BLOCK{ endfor }
  \resumeSubHeadingListEnd
\BLOCK{ endif }

%-----------CERTIFICATIONS-----------------
\BLOCK{ if certifications }
\section{Certifications}
  \resumeSubHeadingListStart
    \BLOCK{ for cert in certifications }
    \resumeSubItem{\VAR{cert.title}}{\VAR{cert.issuer if 'issuer' in cert else ''}}
    \BLOCK{ endfor }
  \resumeSubHeadingListEnd
\BLOCK{ endif }

\end{document}
"""

# -----------------------------------------------------------------------------
# 3. PWC MODERN (Alessandro Rossini / adcv style standalone, Code no 3)
# -----------------------------------------------------------------------------
TEMPLATES["PwC Modern (adcv)"] = r"""\documentclass[a4paper,10pt]{article}

\usepackage[english]{babel}
\usepackage[margin=0.5in]{geometry}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{tabularx}
\usepackage{titlesec}
\usepackage{enumitem}

\definecolor{darkgray}{HTML}{333333}
\definecolor{linegray}{HTML}{CCCCCC}

\titleformat{\section}{
  \vspace{8pt}\large\bfseries\scshape
}{}{0em}{}[\color{linegray}\titlerule \vspace{-3pt}]

\newenvironment{adcvtabletwo}{
  \tabularx{\textwidth}{@{} X r @{}}
}{
  \endtabularx
}

\newcommand{\adcvrowtwo}[2]{
  \textbf{#1} & \small\color{gray}#2 \\
}

\newcommand{\adcvrowmulti}[1]{
  \multicolumn{2}{@{} p{\textwidth} @{}}{\small\color{darkgray}{#1}} \\
}

\newcommand{\adcvrowskip}{\\[4pt]}

\begin{document}

\begin{center}
  {\Huge \bfseries \color{darkgray} \VAR{name}} \\ \vspace{4pt}
  \small \VAR{phone} \quad $\cdot$ \quad \href{mailto:\VAR{email}}{\VAR{email}}
  \BLOCK{ if website } \quad $\cdot$ \quad \href{\VAR{website}}{\VAR{website}} \BLOCK{ endif }
  \BLOCK{ if linkedin } \quad $\cdot$ \quad \href{\VAR{linkedin}}{LinkedIn} \BLOCK{ endif }
  \BLOCK{ if github } \quad $\cdot$ \quad \href{\VAR{github}}{GitHub} \BLOCK{ endif }
\end{center}

\BLOCK{ if summary }
\vspace{4pt}
\small\color{darkgray}\VAR{summary}
\normalsize
\BLOCK{ endif }

\BLOCK{ if experience }
\section{Experience}
\begin{adcvtabletwo}
  \BLOCK{ for exp in experience }
  \adcvrowtwo{\VAR{exp.role}, \VAR{exp.company}, \VAR{exp.location if 'location' in exp else ''}}{\VAR{exp.dates}}
  \BLOCK{ if exp.bullet_points }
  \adcvrowmulti{
    \begin{itemize}[leftmargin=0.15in, label={$\bullet$}, nosep]
      \BLOCK{ for pt in exp.bullet_points }
      \item \VAR{pt}
      \BLOCK{ endfor }
    \end{itemize}
  }
  \BLOCK{ endif }
  \adcvrowskip
  \BLOCK{ endfor }
\end{adcvtabletwo}
\BLOCK{ endif }

\BLOCK{ if projects }
\section{Projects}
\begin{adcvtabletwo}
  \BLOCK{ for proj in projects }
  \adcvrowtwo{\VAR{proj.name} \BLOCK{ if proj.technologies } -- \textit{\VAR{proj.technologies}} \BLOCK{ endif }}{\VAR{proj.dates if 'dates' in proj else ''}}
  \BLOCK{ if proj.bullet_points }
  \adcvrowmulti{
    \begin{itemize}[leftmargin=0.15in, label={$\bullet$}, nosep]
      \BLOCK{ for pt in proj.bullet_points }
      \item \VAR{pt}
      \BLOCK{ endfor }
    \end{itemize}
  }
  \BLOCK{ endif }
  \adcvrowskip
  \BLOCK{ endfor }
\end{adcvtabletwo}
\BLOCK{ endif }

\BLOCK{ if education }
\section{Education}
\begin{adcvtabletwo}
  \BLOCK{ for edu in education }
  \adcvrowtwo{\VAR{edu.degree}, \VAR{edu.institution}, \VAR{edu.location if 'location' in edu else ''}}{\VAR{edu.dates}}
  \adcvrowskip
  \BLOCK{ endfor }
\end{adcvtabletwo}
\BLOCK{ endif }

\BLOCK{ if skills }
\section{Skills}
\begin{itemize}[leftmargin=0.15in, label={}, nosep]
  \small
  \BLOCK{ for cat, list in skills.items() }
  \item \textbf{\VAR{cat}}: \VAR{list | join(', ')}
  \BLOCK{ endfor }
\end{itemize}
\BLOCK{ endif }

\BLOCK{ if certifications }
\section{Certifications}
\begin{adcvtabletwo}
  \BLOCK{ for cert in certifications }
  \adcvrowtwo{\VAR{cert.title} \BLOCK{ if cert.issuer }-- \VAR{cert.issuer}\BLOCK{ endif }}{\BLOCK{ if cert.date }\VAR{cert.date}\BLOCK{ endif }}
  \adcvrowskip
  \BLOCK{ endfor }
\end{adcvtabletwo}
\BLOCK{ endif }

\end{document}
"""

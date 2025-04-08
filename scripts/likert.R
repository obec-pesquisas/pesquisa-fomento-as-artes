if(!require(pacman)) install.packages("pacman")

pacman::p_load(
  readxl, writexl, janitor, likert, ggthemes, table1, flextable, RColorBrewer, googlesheets4, tidyverse
)


# lendo os dados ----------------------------------------------------------

# dados <- read_xlsx("dados/brutos/respostas.xlsx",
#                    sheet = "dados_2024_12_12")
dados <- read_sheet(
  "https://docs.google.com/spreadsheets/d/1_lWu7xqVkmb6BD6-zywttf3VAwmPPx0c7ZyWz40xXoo/edit?usp=sharing",
  sheet = "dados"
)

colunas <- c(
  "def_atvs_valores_lpg_a",
  "def_atvs_valores_lpg_b",
  "def_atvs_valores_lpg_c",
  "def_atvs_valores_lpg_d",
  "def_atvs_valores_lpg_e",
  "def_atvs_valores_lpg_f",
  "how_def_valores_lab_a",
  "how_def_valores_lab_b",
  "how_def_valores_lab_c",
  "how_def_valores_lab_d",
  "how_def_valores_lab_e",
  "how_def_valores_lab_f",
  "processos_decisorios_a",
  "processos_decisorios_b",
  "processos_decisorios_c",
  "processos_decisorios_d",
  "processos_decisorios_e",
  "processos_decisorios_outras"
)
df_all <- dados |>
  filter(eh_capital == 'Estado') |>
  select(
    processos_decisorios_a,
    processos_decisorios_b,
    processos_decisorios_c,
    processos_decisorios_d,
    processos_decisorios_e,
    processos_decisorios_outras,
    how_def_valores_lab_a,
    how_def_valores_lab_b,
    how_def_valores_lab_c,
    how_def_valores_lab_d,
    how_def_valores_lab_e,
    how_def_valores_lab_f,
    def_atvs_valores_lpg_a,
    def_atvs_valores_lpg_b,
    def_atvs_valores_lpg_c,
    def_atvs_valores_lpg_d,
    def_atvs_valores_lpg_e,
    def_atvs_valores_lpg_f
  ) |>
  map_df(~ fct(str_replace(.x,".0", ""), levels = c("N/A", '1', '2', '3', '4', '5'))) |>
  map_df((
    ~ fct_recode(.x, "Não se aplica" = "N/A")
  ))

# processos_decisorios ----------------------------------------------------


df <- df_all |>
  select(processos_decisorios_a,
         processos_decisorios_b,
         processos_decisorios_c,
         processos_decisorios_d,
         processos_decisorios_e,
         processos_decisorios_outras) |>
  rename(
    "(A)" = processos_decisorios_a,
    "(B)" = processos_decisorios_b,
    "(C)" = processos_decisorios_c,
    "(D)" = processos_decisorios_d,
    "(E)" = processos_decisorios_e,
    "Outras" = processos_decisorios_outras,
  ) |>
  as.data.frame()

table1::table1(~ ., data = df, overall = "n (%)", decimal.mark = ",") |>
  table1::t1flex() |>
  flextable::save_as_docx(path = "tabelas/processos_decisorios.docx")

df_graf <- df |>
  likert()

likert.bar.plot(df_graf) +
  labs(y = "Porcentagem") +
  guides(fill = guide_legend(title = "Resposta")) +
  theme_minimal()
ggsave("figuras/processos_decisorios.png", width = 25, height = 10, units = "cm")
ggsave("figuras/processos_decisorios.jpeg", width = 25, height = 10, units = "cm")
ggsave("figuras/processos_decisorios.pdf", width = 25, height = 10, units = "cm")


# how_def_valores_lab -----------------------------------------------------

df <- df_all |>
  select(how_def_valores_lab_a,
         how_def_valores_lab_b,
         how_def_valores_lab_c,
         how_def_valores_lab_d,
         how_def_valores_lab_e,
         how_def_valores_lab_f) |>
  rename(
    "(A)" = how_def_valores_lab_a,
    "(B)" = how_def_valores_lab_b,
    "(C)" = how_def_valores_lab_c,
    "(D)" = how_def_valores_lab_d,
    "(E)" = how_def_valores_lab_e,
    "Outras" = how_def_valores_lab_f,
  ) |>
  as.data.frame()


table1::table1(~ ., data = df, overall = "n (%)", decimal.mark = ",") |>
  table1::t1flex() |>
  flextable::save_as_docx(path = "tabelas/how_def_valores_lab.docx")

df_graf <- df |>
  likert()

likert.bar.plot(df_graf) +
  labs(y = "Porcentagem") +
  guides(fill = guide_legend(title = "Resposta")) +
  theme_minimal()
ggsave("figuras/how_def_valores_lab.png", width = 25, height = 10, units = "cm")
ggsave("figuras/how_def_valores_lab.jpeg", width = 25, height = 10, units = "cm")
ggsave("figuras/how_def_valores_lab.pdf", width = 25, height = 10, units = "cm")


# def_atvs_valores_lpg ----------------------------------------------------


df <- df_all |>
  select(def_atvs_valores_lpg_a,
         def_atvs_valores_lpg_b,
         def_atvs_valores_lpg_c,
         def_atvs_valores_lpg_d,
         def_atvs_valores_lpg_e,
         def_atvs_valores_lpg_f) |>
  rename(
    "(A)" = def_atvs_valores_lpg_a,
    "(B)" = def_atvs_valores_lpg_b,
    "(C)" = def_atvs_valores_lpg_c,
    "(D)" = def_atvs_valores_lpg_d,
    "(E)" = def_atvs_valores_lpg_e,
    "Outras" = def_atvs_valores_lpg_f,
  ) |>
  as.data.frame()


table1::table1(~ ., data = df, overall = "n (%)", decimal.mark = ",") |>
  table1::t1flex() |>
  flextable::save_as_docx(path = "tabelas/def_atvs_valores_lpg.docx")

df_graf <- df |>
  likert()

likert.bar.plot(df_graf) +
  labs(y = "Porcentagem") +
  guides(fill = guide_legend(title = "Resposta")) +
  theme_minimal()
ggsave("figuras/def_atvs_valores_lpg.png", width = 25, height = 10, units = "cm")
ggsave("figuras/def_atvs_valores_lpg.jpeg", width = 25, height = 10, units = "cm")
ggsave("figuras/def_atvs_valores_lpg.pdf", width = 25, height = 10, units = "cm")


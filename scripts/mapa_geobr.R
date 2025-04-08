if (!require(pacman)) install.packages('pacman')
pacman::p_load(
  readxl, writexl, googlesheets4, geobr, tidyverse
)


estados <- read_state()

# valores <- factor(
#   sample(
#     c("Exclusiva", "Conjunta", "Autônoma"),
#     replace = T,
#     size = 27
#   ),
#   levels = c("Exclusiva", "Conjunta", "Autônoma")
# )
# estados['valores'] = valores

df_uf <- read_sheet(
  "https://docs.google.com/spreadsheets/d/1C4Rz416XV5YEz58JoMj6HSlT3-CZ260NYUdoeEMewJI/edit?usp=sharing",
  sheet = "Sheet1"
)

df_estados <- left_join(
  estados,
  df_uf |> select(uf, categorias),
  by = c('abbrev_state' = 'uf')
) |>
  mutate(categorias = fct(categorias,
                          levels = c("Exclusiva", "Conjunta", "Autônoma")))

glimpse(df_estados)

ggplot(df_estados) +
  geom_sf(aes(fill = categorias), linewidth = 1, color = "white",
          show.legend = F) +
  labs(fill = '') +
  scale_fill_manual(values = c("Exclusiva" = "#03664a", "Conjunta" = "#014bb4", "Autônoma" = "#94252c")) +
  annotate("text", -35, -20, label = "Exclusiva", size = 5, color = "#03664a") +
  annotate("text", -35, -22.5, label = "Conjunta", size = 5, color = "#014bb4") +
  annotate("text", -35, -25, label = "Autônoma", size = 5, color = "#94252c") +
  theme_void()
ggsave("figuras/grafico_amanda.png")
ggsave("figuras/grafico_amanda.jpeg")
ggsave("figuras/grafico_amanda.pdf")


# =============================================================================
# PNS 2019 (IBGE) — pessoas com 60 anos ou mais
# Carrega a base filtrada do GitHub, aplica os dicionários e faz análises
# ponderadas com o desenho amostral da pesquisa.
#
# Repositório: https://github.com/adrianomanicoba/dados/tree/main/pns2019_idosos
# Pacote necessário: survey   ->  install.packages("survey")
# =============================================================================

library(survey)
options(survey.lonely.psu = "adjust")  # estratos com uma única UPA

BASE <- "https://raw.githubusercontent.com/adrianomanicoba/dados/main/pns2019_idosos/"

# --- 1. Download e leitura ---------------------------------------------------
baixar <- function(arquivo) {
  destino <- file.path(tempdir(), arquivo)
  if (!file.exists(destino)) download.file(paste0(BASE, arquivo), destino, mode = "wb")
  destino
}

idosos  <- read.csv(gzfile(baixar("pns2019_idosos.csv.gz")),
                    colClasses = c(UPA_PNS = "character", V0024 = "character"))
dic_var <- read.csv(baixar("dicionario_variaveis.csv"), encoding = "UTF-8")
dic_cat <- read.csv(baixar("dicionario_categorias.csv"), encoding = "UTF-8",
                    colClasses = "character")
dic_cat$valor <- trimws(dic_cat$valor)

cat(sprintf("%s moradores com 60+ anos | %s moradores selecionados | %s colunas\n",
            format(nrow(idosos), big.mark = ".", decimal.mark = ","),
            format(sum(idosos$morador_selecionado), big.mark = ".", decimal.mark = ","),
            ncol(idosos)))

# --- 2. Funções de apoio para os dicionários ---------------------------------
# rotulo("K001")  -> descrição da variável
rotulo <- function(v) {
  d <- dic_var$descricao[dic_var$variavel == v]
  if (length(d)) d[1] else v
}

# rotular(idosos$C006, "C006") -> fator com as categorias do IBGE
rotular <- function(x, v) {
  cats <- dic_cat[dic_cat$variavel == v, ]
  if (!nrow(cats)) return(x)
  factor(as.character(x), levels = cats$valor, labels = cats$descricao)
}

# --- 3. Variáveis derivadas ---------------------------------------------------
idosos$sexo         <- rotular(idosos$C006, "C006")
idosos$faixa_etaria <- cut(idosos$C008, c(59, 69, 79, Inf),
                           labels = c("60-69", "70-79", "80+"))

# Atividades básicas da vida diária (módulo K): comer, tomar banho, ir ao banheiro,
# vestir-se, andar em casa, deitar/levantar, sentar/levantar.
# Categorias: 1 Não consegue | 2 Grande dificuldade | 3 Pequena dificuldade | 4 Nenhuma
abvd <- c("K001", "K004", "K007", "K010", "K013", "K016", "K019")
idosos$dificuldade_abvd <- as.integer(rowSums(sapply(idosos[abvd], function(x) x %in% 1:3)) > 0)

# --- 4. Desenhos amostrais ----------------------------------------------------
# a) Todos os moradores 60+ (módulos C a K) -> peso V00281
des_todos <- svydesign(ids = ~UPA_PNS, strata = ~V0024, weights = ~V00281,
                       data = idosos, nest = TRUE)

# b) Moradores selecionados (questionário individual, módulos L em diante) -> peso V00291
sel <- subset(idosos, morador_selecionado == 1)
sel$saude_autoavaliada <- rotular(sel$J001, "J001")
des_sel <- svydesign(ids = ~UPA_PNS, strata = ~V0024, weights = ~V00291,
                     data = sel, nest = TRUE)

# --- 5. Exemplos de análise ---------------------------------------------------
cat("\nPopulação estimada com 60+ anos:",
    format(round(sum(weights(des_todos))), big.mark = ".", decimal.mark = ","), "\n")

cat("\nDistribuição por faixa etária (%):\n")
print(round(100 * prop.table(svytable(~faixa_etaria, des_todos)), 1))

cat("\nDistribuição por sexo (%):\n")
print(round(100 * prop.table(svytable(~sexo, des_todos)), 1))

cat("\nAlguma dificuldade em atividade básica da vida diária, total (%):\n")
m <- svymean(~dificuldade_abvd, des_todos)
print(round(100 * cbind(estimativa = coef(m), confint(m)), 1))

cat("\nAlguma dificuldade em atividade básica da vida diária, por faixa etária (%, IC 95%):\n")
r <- svyby(~dificuldade_abvd, ~faixa_etaria, des_todos, svymean)
print(round(100 * cbind(r[, 2, drop = FALSE], confint(r)), 1))

cat("\n", rotulo("J001"), "(%):\n")
print(round(100 * prop.table(svytable(~saude_autoavaliada, des_sel)), 1))

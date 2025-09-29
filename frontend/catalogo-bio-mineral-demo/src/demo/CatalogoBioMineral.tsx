import * as Accordion from "@radix-ui/react-accordion";
import * as ScrollArea from "@radix-ui/react-scroll-area";
import * as Tabs from "@radix-ui/react-tabs";
import { Separator } from "@radix-ui/react-separator";
import type { ClassValue } from "clsx";
import { clsx } from "clsx";
import {
  Atom,
  Droplets,
  FlaskConical,
  Leaf,
  Layers,
  Sprout,
  ThermometerSun
} from "lucide-react";
import { twMerge } from "tailwind-merge";
import { Fragment } from "react";

const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));

const procesos = [
  {
    id: "biooxidacion",
    label: "Biooxidación",
    descripcion:
      "Pre-tratamiento aeróbico que libera metales refractarios y estabiliza arsénico antes de la lixiviación final.",
    icono: FlaskConical,
    familiasMinerales: [
      {
        nombre: "Sulfuro masivo",
        descripcion:
          "Concentrados de pirita y arsenopirita con oro refractario. Requiere control estricto de Eh y pH.",
        minerales: ["Pirita", "Arsenopirita", "Pirrotina"],
        umbrales: [
          { etiqueta: "Eh", valor: "420–480 mV" },
          { etiqueta: "pH", valor: "1.6 – 1.9" },
          { etiqueta: "Fe(III)", valor: "12 – 18 g/L" }
        ],
        innovaciones: [
          "Reactor multietapa con purga de sólidos", 
          "Control adaptativo DO basado en redox"
        ]
      },
      {
        nombre: "Escorodita",
        descripcion:
          "Generación controlada de escorodita estable para inmovilizar arsénico en corrientes de BIOX.",
        minerales: ["FeAsO₄·2H₂O"],
        umbrales: [
          { etiqueta: "T", valor: "90 – 95 °C" },
          { etiqueta: "pH", valor: "1.5 – 1.7" },
          { etiqueta: "Fe:As", valor: "1.8 – 2.0" }
        ],
        innovaciones: [
          "Semilla sintética para nucleación homogénea",
          "Digestión controlada con microondas"
        ]
      }
    ]
  },
  {
    id: "biolixiviacion",
    label: "Biolixiviación",
    descripcion:
      "Extracción directa de cobre y otros metales a partir de pilas y reactores agitados con consorcios mesófilos o termoacidófilos.",
    icono: Droplets,
    familiasMinerales: [
      {
        nombre: "Sulfuro secundario",
        descripcion:
          "Minerales mixtos de calcosita, covelita y bornita con impurezas de cloruros.",
        minerales: ["Calcosita", "Covelina", "Bornita"],
        umbrales: [
          { etiqueta: "Eh", valor: "420 – 460 mV" },
          { etiqueta: "pH", valor: "1.6 – 1.8" },
          { etiqueta: "% sólidos", valor: "12 – 18" }
        ],
        innovaciones: [
          "Inoculación pulsada con consorcios mixtos",
          "Lavado intermitente para remover cloruros"
        ]
      },
      {
        nombre: "Ni/Co refractario",
        descripcion:
          "Concentrados de pentlandita y cobaltita con ganga silicatada y presencia de Mg.",
        minerales: ["Pentlandita", "Cobaltita", "Violantita"],
        umbrales: [
          { etiqueta: "Eh", valor: "450 – 500 mV" },
          { etiqueta: "pH", valor: "1.5 – 1.7" },
          { etiqueta: "Mg disuelto", valor: "< 4 g/L" }
        ],
        innovaciones: [
          "Quelantes orgánicos para secuestrar Mg",
          "Impulsores termoacidófilos moderados"
        ]
      }
    ]
  },
  {
    id: "biobeneficio",
    label: "Bio-beneficio",
    descripcion:
      "Uso de microorganismos para liberar elementos de tierras raras o eliminar impurezas en circuitos de flotación.",
    icono: Leaf,
    familiasMinerales: [
      {
        nombre: "Fosfatos de REE",
        descripcion:
          "Disolución selectiva de monacita/apatita usando consorcios heterótrofos con producción de ácidos orgánicos.",
        minerales: ["Monacita", "Apatita", "Allanita"],
        umbrales: [
          { etiqueta: "pH", valor: "2.5 – 3.5" },
          { etiqueta: "C fuente", valor: "Lactato 2 – 4 g/L" },
          { etiqueta: "T", valor: "35 – 40 °C" }
        ],
        innovaciones: [
          "Biofilm sobre perlas de alginato",
          "Recuperación de ácidos orgánicos"
        ]
      },
      {
        nombre: "Depresión selectiva",
        descripcion:
          "Control microbiano de superficie para deprimir ganga y activar sulfuros limpios en flotación.",
        minerales: ["Calcita", "Dolomita", "Arcillas"],
        umbrales: [
          { etiqueta: "pH", valor: "7.0 – 8.5" },
          { etiqueta: "Tiempo", valor: "6 – 12 h" },
          { etiqueta: "Redox", valor: "250 – 300 mV" }
        ],
        innovaciones: [
          "Biopolímeros específicos para arcillas",
          "Secuencias de lavado con CO₂"
        ]
      }
    ]
  }
];

const indicadores = [
  {
    icono: Layers,
    etiqueta: "Mineralogía",
    valor: "18 familias",
    detalle: "Matrices QEMSCAN y XRD integradas"
  },
  {
    icono: Atom,
    etiqueta: "Consorcios",
    valor: "12 perfiles",
    detalle: "Balance mesófilos / termoacidófilos"
  },
  {
    icono: ThermometerSun,
    etiqueta: "Ventanas operativas",
    valor: "15 reglas",
    detalle: "Rangos óptimos validados en planta"
  },
  {
    icono: Sprout,
    etiqueta: "Sustentabilidad",
    valor: "-18% ácido",
    detalle: "vs. circuito químico base"
  }
];

const CatalogoBioMineralDemo = () => {
  return (
    <div className="mx-auto w-full max-w-6xl space-y-8 rounded-3xl border border-white/10 bg-slate-900/60 p-10 shadow-2xl shadow-brand/10 backdrop-blur">
      <header className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-3">
          <div className="inline-flex items-center rounded-full border border-brand/40 bg-brand/10 px-4 py-1 text-sm font-semibold uppercase tracking-wide text-brand">
            Catálogo Bio-Mineral
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
            Recetas biohidrometalúrgicas listas para iterar en piloto
          </h1>
          <p className="max-w-2xl text-base text-slate-300">
            Explora familias minerales, ventanas operativas y palancas biológicas
            priorizadas por Eco-Pilot. Cada ficha integra mineralogía, cinética y
            recomendaciones de control para acelerar la toma de decisiones.
          </p>
        </div>
        <div className="grid w-full gap-3 sm:grid-cols-2 lg:w-auto">
          {indicadores.map(({ icono: Icon, etiqueta, valor, detalle }) => (
            <div
              key={etiqueta}
              className="flex min-w-[160px] flex-col gap-1 rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
            >
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <Icon className="h-4 w-4 text-brand" />
                {etiqueta}
              </div>
              <span className="text-xl font-semibold text-white">{valor}</span>
              <span className="text-xs text-slate-400">{detalle}</span>
            </div>
          ))}
        </div>
      </header>

      <Tabs.Root
        defaultValue={procesos[0].id}
        className="overflow-hidden rounded-3xl border border-white/5 bg-slate-950/40"
      >
        <Tabs.List className="flex flex-wrap gap-2 border-b border-white/5 bg-slate-900/80 p-4">
          {procesos.map(({ id, label, descripcion, icono: Icon }) => (
            <Tabs.Trigger
              key={id}
              value={id}
              className={cn(
                "group flex items-center gap-3 rounded-2xl border border-transparent px-4 py-3 text-left text-sm font-medium text-slate-300 transition-all",
                "data-[state=active]:border-brand/40 data-[state=active]:bg-brand/10 data-[state=active]:text-white"
              )}
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-brand/15 text-brand">
                <Icon className="h-5 w-5" />
              </span>
              <span className="flex flex-col gap-1">
                <span>{label}</span>
                <span className="text-xs text-slate-400">{descripcion}</span>
              </span>
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        {procesos.map((proceso) => (
          <Tabs.Content key={proceso.id} value={proceso.id} className="p-6">
            <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
              <ScrollArea.Root className="scroll-area h-[420px] overflow-hidden rounded-2xl border border-white/5 bg-slate-900/60">
                <ScrollArea.Viewport className="h-full w-full p-6">
                  <div className="space-y-6">
                    {proceso.familiasMinerales.map((familia, index) => (
                      <Fragment key={familia.nombre}>
                        <div className="space-y-4">
                          <div className="flex items-start justify-between gap-4">
                            <div>
                              <h3 className="text-xl font-semibold text-white">
                                {familia.nombre}
                              </h3>
                              <p className="mt-1 text-sm text-slate-300">
                                {familia.descripcion}
                              </p>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {familia.minerales.map((mineral) => (
                                <span
                                  key={mineral}
                                  className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200"
                                >
                                  {mineral}
                                </span>
                              ))}
                            </div>
                          </div>

                          <div className="grid gap-4 md:grid-cols-3">
                            <div className="rounded-2xl border border-brand/30 bg-brand/5 p-4">
                              <h4 className="text-xs uppercase tracking-[0.2em] text-brand">
                                Ventanas clave
                              </h4>
                              <ul className="mt-3 space-y-2 text-sm text-slate-200">
                                {familia.umbrales.map((item) => (
                                  <li key={item.etiqueta} className="flex items-center justify-between gap-4">
                                    <span className="text-slate-400">{item.etiqueta}</span>
                                    <span className="font-medium text-white">{item.valor}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>

                            <div className="md:col-span-2">
                              <Accordion.Root type="single" collapsible className="space-y-2">
                                {familia.innovaciones.map((innovacion, idx) => (
                                  <Accordion.Item
                                    key={innovacion}
                                    value={`${familia.nombre}-${idx}`}
                                    className="overflow-hidden rounded-2xl border border-white/10 bg-white/5"
                                  >
                                    <Accordion.Header>
                                      <Accordion.Trigger className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left text-sm font-medium text-white transition hover:bg-white/5">
                                        <span>{innovacion}</span>
                                        <span className="text-xs text-slate-400">Detalle</span>
                                      </Accordion.Trigger>
                                    </Accordion.Header>
                                    <Accordion.Content className="px-4 pb-4 text-sm text-slate-300">
                                      Profundiza en la implementación con hojas de proceso,
                                      cultivos recomendados y parámetros cinéticos validados.
                                    </Accordion.Content>
                                  </Accordion.Item>
                                ))}
                              </Accordion.Root>
                            </div>
                          </div>
                        </div>
                        {index < proceso.familiasMinerales.length - 1 && (
                          <Separator className="my-6 h-px bg-white/5" />
                        )}
                      </Fragment>
                    ))}
                  </div>
                </ScrollArea.Viewport>
                <ScrollArea.Scrollbar
                  orientation="vertical"
                  className="flex h-full w-2 touch-none select-none bg-transparent"
                >
                  <ScrollArea.Thumb className="relative flex-1 rounded-full bg-brand/40" />
                </ScrollArea.Scrollbar>
              </ScrollArea.Root>

              <div className="space-y-6 rounded-2xl border border-white/5 bg-slate-900/40 p-6">
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-white">Qué monitorear</h3>
                  <p className="text-sm text-slate-300">
                    Indicadores críticos recomendados por Eco-Pilot para mantener
                    la biocatalisis estable y segura en la ruta {proceso.label.toLowerCase()}.
                  </p>
                </div>
                <ul className="space-y-3 text-sm text-slate-200">
                  <li>
                    <span className="font-medium text-white">Balance redox dinámico:</span>
                    &nbsp;ajusta aireación y lixiviantes según el gradiente Eh real vs. objetivo.
                  </li>
                  <li>
                    <span className="font-medium text-white">Huella microbiana:</span>
                    &nbsp;valida consorcios por qPCR y secuenciación ligera semanal.
                  </li>
                  <li>
                    <span className="font-medium text-white">Cierre de agua:</span>
                    &nbsp;optimiza recirculación minimizando sulfatos y cloruros acumulados.
                  </li>
                </ul>

                <div className="rounded-2xl border border-brand/30 bg-brand/10 p-5 text-sm text-brand-foreground">
                  <p className="font-semibold text-brand-foreground">
                    Siguiente paso sugerido
                  </p>
                  <p className="mt-2 text-brand-foreground/80">
                    Sincroniza este módulo con el optimizador de recetas para simular escenarios de consumo ácido y extracción metal vs. riesgo arsenical.
                  </p>
                </div>
              </div>
            </div>
          </Tabs.Content>
        ))}
      </Tabs.Root>
    </div>
  );
};

export { CatalogoBioMineralDemo };

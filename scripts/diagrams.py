import codecs
import sys
import sadisplay  # type: ignore
from pathlib import Path

HERE = Path(__file__).parent
sys.path.append(str(HERE / "../"))


from app import models as model  # noqa

# desc = sadisplay.describe(
#     [getattr(model, attr) for attr in dir(model)],
#     show_methods=True,
#     show_properties=True,
#     show_indexes=True,
# )
# with codecs.open("schema.plantuml", "w", encoding="utf-8") as f:
#     f.write(sadisplay.plantuml(desc))
# with codecs.open("schema.dot", "w", encoding="utf-8") as f:
#     f.write(sadisplay.dot(desc))

# Or only part of schema
desc = sadisplay.describe(
    [
        model.ClusterGraph,
        model.ClusterOneLogParams,
        model.Edge,
        model.EdgePPIInteraction,
        model.Layout,
        model.PPIGraph,
        model.Protein,
        model.Proteome,
        model.EdgeClusterInteraction,
        model.Enrichment,
        model.GoTerms,
        model.OverlappingProtein,
    ]
)
with codecs.open("no_overlapping_protein.plantuml", "w", encoding="utf-8") as f:  # noqa
    f.write(sadisplay.plantuml(desc))
with codecs.open("no_overlapping_protein.dot", "w", encoding="utf-8") as f:
    f.write(sadisplay.dot(desc))

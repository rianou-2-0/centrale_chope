import pandas as pd
import networkx as nx
from pyvis.network import Network

# --- 1. CONFIGURATION DU GOOGLE SHEET ---
SHEET_ID = "13qV-mhDlUloySMoqU6YBwDNdSDjocfXbVNz99RTtVT0"
GID = "390021334"
# URL magique pour télécharger l'onglet directement en CSV
url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"


# --- 2. CATÉGORIES ET COULEURS (En dur pour le moment) ---
groupes = {
    "CentraleH": ["Alan", "Antoine", "Anton", "Arsène", "Arthur", "Bastien", "Bastien Nostra", "Clem Neuil", "Ethan", "Etienne", "Étienne", "Florian", "Hugo Thubes", "Jules", "Lucien", "Marin Yards", "Martin", "Matteo", "Mehdi", "Matthias", "Maxime", "Milan", "Nowa", "Paul", "Roméo",  "Sacha", "Simon", "Tao", "Ulysse", "Virgile", "Romain"],
    "CentraleF": ["Amandine",  "Belen", "Cléa", "Coline", "Elisa", "Faustine", "Jade", "Jasmine", "Joséphine", "Juliette Bross", "Kimlan", "Laure", "Lisa", "Lorraine", "Louise G3 césuré", "Lucie", "Nina", "Ninon",  "Noémie", "Rulin", "Sarah", "Sophie", "Yasmine"],
    "IteemH": ["Nathanaël", "Pacôme", "William"],
    "IteemF": ["Camille", "Juliette Iteem", "Margaux", "Nina Iteem", "Lila"],
    "ChimieH" : ["Thibault"],
    "ChimieF" : ["Cléo", "Ellina", "Jeanne Mads"],
    "Autre": ["Clara Joy", "Giono", "Lise-Anaïs Joy", "Leandre", "Marceau CS", "Meuf The Room", "Meuf la catho 1", "Meuf la catho 2", "Oscar Pote de Lucien", "Roméo CS"]
}

color_map = {
    "CentraleH": "#3e84ca", "CentraleF": "#66b3ff", 
    "IteemH": "#00954A", "IteemF": "#00cc66", 
    "ChimieH": "#ff9705", "ChimieF": "#ffcc00", 
    "Autre": "#cccccc"
}
DEFAULT_COLOR = "#cccccc"


# --- 3. RÉCUPÉRATION DES DONNÉES ---
try:
    # On lit le CSV. pandas va détecter automatiquement les colonnes "Homme" et "Fille"
    df = pd.read_csv(url_csv)
    # On supprime les lignes vides au cas où
    df = df.dropna(subset=['Homme', 'Fille'])
except Exception as e:
    print(f"Erreur lors de la lecture du Google Sheet : {e}")
    exit(1)


# --- 4. CALCULS RÉSEAU ---
G = nx.Graph()

# Ajout des liens à partir des colonnes "Homme" et "Fille"
for index, row in df.iterrows():
    source = str(row['Homme']).strip()
    target = str(row['Fille']).strip()
    G.add_edge(source, target)

degrees = dict(G.degree())


# --- 5. CONFIGURATION WEB ---
net = Network(height="90vh", width="100%", bgcolor="#ffffff", font_color="black", directed=False, cdn_resources='in_line')

net.set_options("""
var options = {
  "nodes": { "shape": "circle", "font": { "size": 14, "face": "tahoma", "color": "black" }, "borderWidth": 2, "scaling": { "min": 25, "max": 80, "label": { "enabled": true, "min": 14, "max": 24 } } },
  "edges": { "smooth": { "type": "curvedCW", "roundness": 0.15 }, "arrows": { "to": { "enabled": false } } },
  "physics": { "forceAtlas2Based": { "gravitationalConstant": -80, "centralGravity": 0.01, "springLength": 80, "springConstant": 0.08, "avoidOverlap": 0.5, "damping": 1 }, "minVelocity": 0.75, "solver": "forceAtlas2Based", "stabilization": { "enabled": true, "iterations": 2000, "updateInterval": 25, "fit": true } },
  "interaction": { "hover": true, "multiselect": true }
}
""")


# --- 6. ATTRIBUTION DES COULEURS ET AJOUT AU GRAPHE ---
for node in G.nodes():
    # Chercher à quel groupe appartient la personne
    node_color = DEFAULT_COLOR
    for groupe, membres in groupes.items():
        if node in membres:
            node_color = color_map[groupe]
            break
            
    deg = degrees.get(node, 1)
    net.add_node(node, label=node, title=f"{node} : {deg} connexions", color=node_color, value=deg)

for source, target in G.edges():
    # Par défaut, le lien prend la couleur de la cible (Fille) pour garder ta logique initiale
    edge_color = DEFAULT_COLOR
    for groupe, membres in groupes.items():
        if target in membres:
            edge_color = color_map[groupe]
            break
    net.add_edge(source, target, color=edge_color)


# --- 7. INJECTION DU SCRIPT HIGHLIGHT ET SAUVEGARDE ---
custom_js = """
<script type="text/javascript">
    network.on("click", function (params) {
        var allNodes = nodes.get();
        var allEdges = edges.get();
        
        if (params.nodes.length > 0) {
            var clickedNodeId = params.nodes[0];
            var connectedNodes = network.getConnectedNodes(clickedNodeId);
            var connectedEdges = network.getConnectedEdges(clickedNodeId);
            
            var newNodes = [];
            for (var i = 0; i < allNodes.length; i++) {
                var node = allNodes[i];
                if (node.originalColor === undefined) { node.originalColor = node.color; }
                if (node.id == clickedNodeId || connectedNodes.includes(node.id)) { node.color = node.originalColor; } 
                else { node.color = 'rgba(200,200,200,0.3)'; }
                newNodes.push(node);
            }
            nodes.update(newNodes);
            
            var newEdges = [];
            for (var i = 0; i < allEdges.length; i++) {
                var edge = allEdges[i];
                if (edge.originalColor === undefined) { edge.originalColor = edge.color; }
                if (connectedEdges.includes(edge.id)) { edge.color = edge.originalColor; } 
                else { edge.color = 'rgba(200,200,200,0.8)'; }
                newEdges.push(edge);
            }
            edges.update(newEdges);
        } else {
            var newNodes = [];
            for (var i = 0; i < allNodes.length; i++) {
                var node = allNodes[i];
                if (node.originalColor !== undefined) { node.color = node.originalColor; newNodes.push(node); }
            }
            nodes.update(newNodes);
            
            var newEdges = [];
            for (var i = 0; i < allEdges.length; i++) {
                var edge = allEdges[i];
                if (edge.originalColor !== undefined) { edge.color = edge.originalColor; newEdges.push(edge); }
            }
            edges.update(newEdges);
        }
    });
</script>
"""

output_file = "index.html"
html_content = net.generate_html()
html_content = html_content.replace('</body>', custom_js + '</body>')

with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Graphe généré avec succès à partir du Google Sheet !")

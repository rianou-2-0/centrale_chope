import pandas as pd
import networkx as nx
from pyvis.network import Network

# --- 1. CONFIGURATION DU GOOGLE SHEET ---
SHEET_ID = "13qV-mhDlUloySMoqU6YBwDNdSDjocfXbVNz99RTtVT0"
GID = "390021334"
url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

# --- 2. COULEURS ---
color_map = {
    "CentraleH": "#3e84ca", "CentraleF": "#66b3ff", 
    "IteemH": "#00954A", "IteemF": "#00cc66", 
    "ChimieH": "#ff9705", "ChimieF": "#ffcc00", 
    "Autre": "#cccccc"
}
DEFAULT_COLOR = "#808080"

# --- 3. RÉCUPÉRATION DES DONNÉES ---
try:
    df = pd.read_csv(url_csv)
    
    # On utilise l'index des colonnes pour être robuste (0=Homme, 1=Cat_H, 2=Fille, 3=Cat_F)
    cols = df.columns
    col_homme = cols[0]
    col_cat_h = cols[1]
    col_fille = cols[2]
    col_cat_f = cols[3]
    
    # Suppression des lignes où il n'y a ni Homme ni Fille
    df = df.dropna(subset=[col_homme, col_fille])
except Exception as e:
    print(f"Erreur lors de la lecture du Google Sheet : {e}")
    exit(1)

# --- 4. EXTRACTION DES CATÉGORIES ET CALCULS RÉSEAU ---
G = nx.Graph()
category_dict = {}

for index, row in df.iterrows():
    homme = str(row[col_homme]).strip()
    fille = str(row[col_fille]).strip()
    
    # Récupération de la catégorie Homme (si elle existe et n'est pas vide)
    cat_h = str(row[col_cat_h]).strip()
    if cat_h and cat_h.lower() != 'nan':
        category_dict[homme] = cat_h
        
    # Récupération de la catégorie Fille (si elle existe et n'est pas vide)
    cat_f = str(row[col_cat_f]).strip()
    if cat_f and cat_f.lower() != 'nan':
        category_dict[fille] = cat_f

    # Ajout du lien
    G.add_edge(homme, fille)

degrees = dict(G.degree())

# --- 5. CONFIGURATION WEB ---
net = Network(height="90vh", width="100%", bgcolor="#ffffff", font_color="black", directed=False, cdn_resources='in_line')
net.set_options("""
var options = {
  "nodes": {
    "borderWidth": 2,
    "font": {
      "color": "black",
      "face": "tahoma",
      "size": 14
    },
    "scaling": {
      "min": 30,
      "max": 100,
      "label": {
        "enabled": true,
        "min": 14,
        "max": 24
      }
    },
    "shape": "circle"
  },
  "edges": {
    "smooth": {
      "type": "curvedCW",
      "roundness": 0.15
    },
    "arrows": { 
      "to": { "enabled": false } 
    }
  },
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -80,
      "centralGravity": 0.01,
      "springLength": 80,
      "springConstant": 0.08,
      "avoidOverlap": 0.5,
      "damping": 1
    },
    "minVelocity": 0.75,
    "solver": "forceAtlas2Based",
    "stabilization": {
      "enabled": true,
      "iterations": 2000,
      "updateInterval": 25,
      "fit": true
    }
  },
  "interaction": {
    "hover": true,
    "multiselect": true
  }
}
""")

# --- 6. ATTRIBUTION DES COULEURS ET AJOUT AU GRAPHE ---
for node in G.nodes():
    # Cherche la catégorie du noeud, sinon applique "Inconnu" et la couleur par défaut
    groupe = category_dict.get(node, "Inconnu")
    node_color = color_map.get(groupe, DEFAULT_COLOR)
    deg = degrees.get(node, 1)
    
    net.add_node(node, label=node, title=f"{node} : {deg} connexions ({groupe})", color=node_color, value=deg)

for source, target in G.edges():
    # Le lien prend la couleur de la cible (Fille)
    groupe_target = category_dict.get(target, "Inconnu")
    edge_color = color_map.get(groupe_target, DEFAULT_COLOR)
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

print("Graphe généré avec succès à partir du nouveau Google Sheet !")

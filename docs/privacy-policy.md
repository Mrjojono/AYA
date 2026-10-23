# Politique de confidentialité d'Aya

> **Brouillon à faire relire.** Les passages entre crochets `[ ]` restent à confirmer avant publication. Ce texte doit être relu par un conseiller juridique. Il décrit Aya telle qu'elle est conçue aujourd'hui ; si le fonctionnement change, on met ce texte à jour.

**Dernière mise à jour :** [JJ/MM/AAAA]

---

## En bref

Aya vous aide à repérer les combinaisons d'aliments et de médicaments qui peuvent poser problème. Pour cela, elle doit traiter des informations sur ce que vous mangez et ce que vous prenez, et certaines de ces informations touchent à votre santé. Nous voulons que vous sachiez exactement ce qui se passe avec, pourquoi, et comment vous gardez la main.

- Nous ne vendons jamais vos données, et nous ne les utilisons pas pour de la publicité.
- Vous n'avez pas besoin de compte pour utiliser Aya.
- Vous pouvez voir, exporter ou supprimer vos données à tout moment.
- Aya ne remplace pas un médecin ni un pharmacien.

---

## 1. Qui est responsable de vos données

Le responsable du traitement est [nom de la personne ou de l'organisation], joignable à [adresse e-mail].

## 2. Ce que nous collectons

Nous ne collectons que ce qui sert à faire fonctionner Aya.

**Votre profil (facultatif, sauf l'âge).** Âge, poids, taille, conditions de santé que vous choisissez de déclarer (par exemple diabète ou hypertension), allergies alimentaires, régime particulier, et médicaments que vous prenez régulièrement. Ce sont des informations de santé. Nous ne les demandons que si vous choisissez de les renseigner, et vous pouvez les modifier ou les supprimer quand vous voulez.

**Vos repas.** Ce que vous enregistrez, sous forme de texte, de voix, de photo ou de code-barres. Pour un repas enregistré par la voix, nous conservons le résultat de la transcription. Pour les photos, voir la section 4.

**Votre historique.** Les repas enregistrés, les totaux de la journée et de la semaine, et les alertes affichées.

**Des données techniques.** Un identifiant de session anonyme, pour que votre appareil reste connecté sans compte. Il ne contient pas votre nom.

**Vos corrections et vos réponses aux enquêtes.** Si vous corrigez un aliment mal reconnu ou répondez à une question après une alerte, nous gardons cette réponse pour améliorer Aya. Les enquêtes sont optionnelles.

## 3. Pourquoi nous les utilisons

- Pour identifier ce que vous mangez, calculer les nutriments et vérifier les combinaisons.
- Pour afficher votre historique et vos totaux.
- Pour améliorer la reconnaissance des aliments, des plats et des noms locaux, à partir de vos corrections.
- Pour protéger le service contre les abus, par exemple en limitant le nombre de requêtes.

Nous ne faisons rien d'autre avec vos informations.

## 4. Vos photos et votre voix

Quand vous prenez une photo ou enregistrez votre voix, ces fichiers sont envoyés à notre serveur pour être traités.

- **Les photos** servent à identifier le repas ou l'étiquette. Elles sont supprimées une fois l'identification faite, sauf si vous choisissez de les garder.
- **Les enregistrements vocaux** servent à la transcription. [Préciser : durée de conservation de l'audio, et s'il est supprimé après transcription.]
- **L'usage pour améliorer les modèles** (par exemple pour mieux reconnaître les noms de plats locaux) n'est possible qu'avec votre accord explicite, et seulement après anonymisation. [À confirmer : si cet usage est prévu dans la première version.]

## 5. Qui d'autre traite vos données

Aya fait appel à des services extérieurs. Nous vous les présentons pour que vous sachiez qui intervient.

- **Hébergement** : le serveur et la base de données sont hébergés chez [fournisseur], à [pays ou région]. La base de données utilise PostgreSQL, et le cache utilise Redis.
- **Modèles d'intelligence artificielle** (transcription vocale, traduction, extraction des aliments, reconnaissance des plats) : [indiquer si ces modèles tournent sur nos propres serveurs, ou chez un fournisseur extérieur. Si un fournisseur reçoit vos données, le nommer ici.]
- **Bases de données alimentaires et médicales** : Open Food Facts pour les produits emballés, et openFDA pour les notices de médicaments. Ces services reçoivent des requêtes, par exemple un code-barres ou un nom de médicament, mais pas votre nom ni votre identifiant. [À confirmer : ce qui est transmis exactement.]

Nous ne vendons pas vos données et nous ne les partageons pas avec des annonceurs.

## 6. Sur les sources d'Aya

Aya ne valide pas elle-même les interactions. Elle applique des règles tirées de sources publiques, et indique à chaque fois d'où vient l'information :

- **DrugBank** pour les interactions entre médicaments, sous licence académique non commerciale. C'est pour cette raison qu'Aya reste gratuite et non commerciale.
- **openFDA** pour les notices officielles de médicaments.
- **Open Food Facts** pour les fiches produits, sous licence ouverte.
- **WAFCT 2019** (*West African Food Composition Table*) pour la composition des aliments ouest-africains. [À vérifier : formule d'attribution exacte.]
- **Recommandations de l'OMS et de la FAO (2004)** pour les seuils nutritionnels.

Ces sources ne reçoivent pas vos données personnelles. Leur qualité dépend de leur mise à jour, et Aya le signale quand une information est ancienne ou incertaine.

## 7. Où vos données sont conservées, et combien de temps

- **Votre profil et votre historique** : jusqu'à ce que vous les supprimiez, ou que vous supprimiez votre session.
- **Vos photos** : supprimées après identification, sauf si vous les gardez.
- **Vos enregistrements vocaux** : [durée].
- **Les journaux techniques** : [X jours], puis supprimés.
- **Votre session** : elle expire après [durée] d'inactivité.

Quand vous supprimez vos données, elles disparaissent de nos bases de production. Les sauvegardes sont effacées dans un délai de [X jours].

## 8. La sécurité

Vos données de santé sont chiffrées pendant le transport (TLS) et conservées dans une base chiffrée. Les clés d'accès aux services extérieurs sont gardées à part, jamais dans le code. Nos journaux sont nettoyés : les e-mails, les jetons et les identifiants d'appareil sont masqués ou tronqués. Personne ne peut garantir une sécurité absolue, mais nous faisons tout pour réduire les risques, et nous vous préviendrons si un incident touche vos données.

## 9. Cookies et traceurs

Aya n'utilise ni publicité ni outil de suivi. Le seul élément stocké sur votre téléphone est le jeton qui maintient votre session. [À confirmer : aucun outil d'analyse.]

## 10. Enfants et adolescents

[À définir : par exemple, « Aya n'est pas destinée aux moins de [âge] ans. Si vous êtes parent ou tuteur et que vous pensez qu'un mineur nous a transmis des informations, écrivez-nous à [e-mail] et nous les supprimerons. »]

## 11. Votre consentement

Au premier lancement, Aya vous demande votre accord. Ce texte vous explique ce que nous collectons, pourquoi, et comment vous pouvez revenir sur votre choix. Pour les données de santé, cet accord est explicite. Vous pouvez le retirer à tout moment dans les réglages, et Aya continuera de fonctionner pour le reste.

## 12. Vos droits

Vous pouvez à tout moment :

- **voir** les données que nous avons sur vous ;
- **corriger** celles qui sont fausses ;
- **supprimer** votre profil, votre historique ou votre session ;
- **exporter** vos données dans un format lisible ;
- **retirer votre consentement** à un traitement précis ;
- **vous opposer** à un usage ou demander à le limiter.

Pour cela, il vous suffit de nous écrire à [adresse e-mail]. Nous répondons dans un délai de [X jours].

Si vous estimez que vos droits ne sont pas respectés, vous pouvez saisir l'autorité compétente. Au Togo, il s'agit de [autorité, à confirmer au regard de la loi n° 2019-014 relative à la protection des données à caractère personnel].

## 13. Les changements

Si cette politique change de manière importante, nous vous le dirons dans l'application avant qu'elle entre en vigueur. La date en haut de la page indique la version actuelle.

## 14. Nous contacter

Une question sur vos données ? Écrivez-nous à [adresse e-mail]. Nous lisons chaque message et nous répondons de façon claire.

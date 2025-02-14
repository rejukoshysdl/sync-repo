  (async () => {
    const fetch = (await import("node-fetch")).default;

    const SOURCE_SHOPIFY_STORE = "mb-stg.myshopify.com";
    const SOURCE_ACCESS_TOKEN = "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";

    const DESTINATION_SHOPIFY_STORE = "mbdev09.myshopify.com";
    const DESTINATION_ACCESS_TOKEN = "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";

    let metaobjectMappings = {}; // Stores metaobject type → ID mappings

    /**
     * Fetch all metaobject definitions from the destination store
     * Creates missing metaobjects if requiredTypes contains unknown types.
     */
    async function fetchMetaobjectDefinitions(requiredTypes) {
      const query = `{
        metaobjectDefinitions(first: 100) {
          edges {
            node {
              id
              type
            }
          }
        }
      }`;

      const response = await fetch(`https://${DESTINATION_SHOPIFY_STORE}/admin/api/2024-01/graphql.json`, {
        method: "POST",
        headers: {
          "X-Shopify-Access-Token": DESTINATION_ACCESS_TOKEN,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const result = await response.json();

      if (result.errors) {
        console.error("❌ Error fetching metaobject definitions:", result.errors);
        return;
      }

      // Store existing metaobject definitions
      metaobjectMappings = result.data.metaobjectDefinitions.edges.reduce((acc, edge) => {
        acc[edge.node.type] = edge.node.id;
        return acc;
      }, {});

      console.log("✅ Fetched Metaobject Definitions:", metaobjectMappings);

      // Check for missing metaobject types and create them
      for (const type of requiredTypes) {
        if (!metaobjectMappings[type]) {
          console.log(`⚠️ Missing metaobject definition: ${type}, creating now...`);
          const newId = await createMetaobjectDefinition(type);
          if (newId) {
            metaobjectMappings[type] = newId;
          }
        }
      }
    }

    /**
     * Create a metaobject definition in the destination store
     */
    async function createMetaobjectDefinition(type) {
      const mutation = `mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
        metaobjectDefinitionCreate(definition: $definition) {
          metaobjectDefinition {
            id
            type
          }
          userErrors {
            field
            message
          }
        }
      }`;

      const response = await fetch(`https://${DESTINATION_SHOPIFY_STORE}/admin/api/2024-01/graphql.json`, {
        method: "POST",
        headers: {
          "X-Shopify-Access-Token": DESTINATION_ACCESS_TOKEN,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: mutation,
          variables: {
            definition: {
              type: type,
              name: type.replace("_", " ").toUpperCase(),
            },
          },
        }),
      });

      const result = await response.json();

      if (result.errors || result.data.metaobjectDefinitionCreate.userErrors.length > 0) {
        console.error(`❌ Error creating metaobject definition for: ${type}`, result.errors || result.data.metaobjectDefinitionCreate.userErrors);
        return null;
      } else {
        console.log(`✅ Successfully created metaobject definition: ${type}`);
        return result.data.metaobjectDefinitionCreate.metaobjectDefinition.id;
      }
    }

    /**
     * Fetch all metafield definitions from the source store
     */
    async function getMetafieldDefinitions() {
      const query = `{
        metafieldDefinitions(first: 250, ownerType: PRODUCT) {
          edges {
            node {
              id
              name
              namespace
              key
              type {
                name
                category
              }
              description
            }
          }
        }
      }`;

      const response = await fetch(`https://${SOURCE_SHOPIFY_STORE}/admin/api/2024-01/graphql.json`, {
        method: "POST",
        headers: {
          "X-Shopify-Access-Token": SOURCE_ACCESS_TOKEN,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const result = await response.json();

      if (result.errors) {
        console.error("❌ Error fetching metafield definitions:", result.errors);
        return [];
      }

      return result.data.metafieldDefinitions.edges.map(edge => edge.node);
    }

    /**
     * Delete an existing metafield definition before recreating it
     */
    async function deleteExistingMetafield(metafield) {
      const metafieldId = await getMetafieldId(metafield);
      if (!metafieldId) return;

      const mutation = `mutation DeleteMetafieldDefinition($id: ID!) {
        metafieldDefinitionDelete(id: $id) {
          deletedId
          userErrors {
            field
            message
          }
        }
      }`;

      await fetch(`https://${DESTINATION_SHOPIFY_STORE}/admin/api/2024-01/graphql.json`, {
        method: "POST",
        headers: {
          "X-Shopify-Access-Token": DESTINATION_ACCESS_TOKEN,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: mutation,
          variables: { id: metafieldId },
        }),
      });

      console.log(`✅ Deleted existing metafield: ${metafield.key}`);
    }

    /**
     * Create a metafield definition in the destination store
     */
    async function createMetafieldDefinition(metafield) {
      const mutation = `mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
        metafieldDefinitionCreate(definition: $definition) {
          createdDefinition {
            id
            name
            namespace
            key
            type {
              name
              category
            }
            description
            ownerType
            validations {
              type
              value
            }
          }
          userErrors {
            field
            message
          }
        }
      }`;

      const metafieldType = metafield.type?.name || "single_line_text_field";
      const isMetaobject = metafieldType.includes("metaobject_reference");
      const metaobjectId = isMetaobject ? metaobjectMappings[metafieldType.replace("list.", "")] || null : null;

      const namespace = metafield.namespace.startsWith("shopify.") 
  ? "custom_" + metafield.namespace.split(".")[1] 
  : metafield.namespace;

      const response = await fetch(`https://${DESTINATION_SHOPIFY_STORE}/admin/api/2024-01/graphql.json`, {
        method: "POST",
        headers: {
          "X-Shopify-Access-Token": DESTINATION_ACCESS_TOKEN,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: mutation,
          variables: {
            definition: {
              name: metafield.name,
              namespace: namespace,
              key: metafield.key,
              type: metafieldType,
              description: metafield.description || "",
              ownerType: "PRODUCT",
              validations: metaobjectId ? [{ type: "metaobject_definition_id", value: metaobjectId }] : [],
            },
          },
        }),
      });

      const result = await response.json();

      if (result.errors || result.data.metafieldDefinitionCreate.userErrors.length > 0) {
        console.error(`❌ Error creating metafield: ${metafield.key}`, result.errors || result.data.metafieldDefinitionCreate.userErrors);
      } else {
        console.log(`✅ Successfully created metafield: ${metafield.key}`);
      }
    }

    /**
     * Migrate metafield definitions from source to destination store
     */
    async function migrateMetafields() {
      console.log("🔄 Fetching metafield definitions from source store...");
      const metafields = await getMetafieldDefinitions();
      if (metafields.length === 0) return;

      const requiredTypes = [...new Set(metafields.filter(m => m.type.name.includes("metaobject_reference")).map(m => m.type.name.replace("list.", "")))];

      console.log("🔄 Fetching metaobject definitions...");
      await fetchMetaobjectDefinitions(requiredTypes);

      for (const metafield of metafields) {
      //  await deleteExistingMetafield(metafield);
        await createMetafieldDefinition(metafield);
      }

      console.log("🎉 Metafield migration completed!");
    }
    migrateMetafields();
  })();

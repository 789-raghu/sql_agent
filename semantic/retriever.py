from typing import List, Dict, Any, Set
from semantic.schema_catalog import SCHEMA_CATALOG
from semantic.relationships import RELATIONSHIPS
from semantic.definitions import BUSINESS_DEFINITIONS
import structlog

logger = structlog.get_logger()


class SchemaRetriever:
    def __init__(self, catalog: Dict[str, Dict[str, Any]] = SCHEMA_CATALOG, relationships: List[Dict[str, str]] = RELATIONSHIPS):
        self.catalog = catalog
        self.relationships = relationships

    def retrieve(self, question: str) -> Dict[str, Any]:
        """
        Determines relevant database tables, columns, and relationships based on question keywords.
        Returns dictionary containing relevant_tables, schema_prompt_text, and relationships.
        """
        q_lower = question.lower()
        selected_tables: Set[str] = set()

        # Analytics / Summary Table Keywords (public schema)
        if any(w in q_lower for w in ["prediction", "predicted", "forecast", "compare"]):
            selected_tables.update(["predictions", "consumption", "consumers", "consumer_predictions"])
        if any(w in q_lower for w in ["cluster", "zone", "region"]):
            selected_tables.update(["clusters", "consumers", "consumer_cluster_summary"])
        if any(w in q_lower for w in ["location", "city", "state"]):
            selected_tables.update(["locations", "consumers"])
        if any(w in q_lower for w in ["daily", "yesterday", "last week", "summary", "highest", "average", "top"]):
            selected_tables.update(["consumption", "daily_summary", "consumers", "consumer_daily_summary"])
        if "july" in q_lower or "month" in q_lower:
            selected_tables.update(["consumption", "daily_summary", "consumers", "consumer_monthly_summary"])

        # Data Lake Schema Keywords (epdatalake schema)
        if any(w in q_lower for w in ["dtr", "transformer", "struc_code", "structure code"]):
            selected_tables.update(["epdatalake.dtr_master", "epdatalake.consumer_mapping"])
        if any(w in q_lower for w in ["amr", "blp", "fdr_dtr", "t_nw_blp"]):
            selected_tables.update(["epdatalake.fdr_dtr_newcharge", "epdatalake.t_nw_blp", "epdatalake.consumer_mapping"])
        if any(w in q_lower for w in ["smart meter", "smart_meter", "ukscno", "mtr_sno", "1-phase", "3-phase", "single phase", "three phase", "t_blp_sp", "t_blp_tp"]):
            selected_tables.update(["epdatalake.lt_consumer_master", "epdatalake.smart_meters_install_m", "epdatalake.t_blp_sp", "epdatalake.t_blp_tp"])
        if any(w in q_lower for w in ["lt consumer", "scno", "non-smart", "lt_meter_data", "present reading", "prev reading"]):
            selected_tables.update(["epdatalake.lt_consumer_master", "epdatalake.lt_meter_data", "epdatalake.consumer_mapping"])
        if any(w in q_lower for w in ["ht consumer", "ht", "high tension", "contract demand", "supply voltage", "ht_consumer_master"]):
            selected_tables.update(["epdatalake.ht_consumer_master"])
        if any(w in q_lower for w in ["bill", "billing", "billed amount", "invoice"]):
            selected_tables.update(["epdatalake.lt_billing_data", "epdatalake.htbpbillprocess_t", "epdatalake.oracle.smart_meters_billdata"])
        if any(w in q_lower for w in ["category", "cat_code", "tariff"]):
            selected_tables.update(["epdatalake.lt_category_master", "epdatalake.lt_consumer_master"])

        # Default fallback if no specific keywords matched
        if not selected_tables:
            selected_tables.update(["consumers", "consumption", "daily_summary"])

        # Gather schema strings for selected tables
        schema_parts = []
        for table in sorted(selected_tables):
            if table in self.catalog:
                info = self.catalog[table]
                schema_parts.append(f"TABLE: {table}")
                schema_parts.append(f"Description: {info['description']}")
                schema_parts.append("Columns:")
                for col, desc in info["columns"].items():
                    schema_parts.append(f"  - {col}: {desc}")
                schema_parts.append("")

        # Gather applicable relationships
        relevant_rels = []
        for rel in self.relationships:
            if rel["from_table"] in selected_tables or rel["to_table"] in selected_tables:
                relevant_rels.append(f"- {rel['from_table']} JOIN {rel['to_table']} ON {rel['join_condition']}")

        schema_prompt_text = "\n".join(schema_parts)
        rel_prompt_text = "\n".join(relevant_rels)

        logger.info("Schema retrieved", question=question, tables=list(selected_tables))

        return {
            "relevant_tables": sorted(list(selected_tables)),
            "schema_prompt": schema_prompt_text,
            "relationships_prompt": rel_prompt_text,
            "definitions_prompt": BUSINESS_DEFINITIONS
        }


schema_retriever = SchemaRetriever()

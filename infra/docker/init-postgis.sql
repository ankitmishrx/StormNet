-- ==============================================================================
-- STORMNET — PostGIS Database Initialization Script
-- Convective Scale Nowcasting Platform (SIH26084)
-- ==============================================================================

-- Enable PostGIS spatial extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify PostGIS version
DO $$
BEGIN
    RAISE NOTICE 'PostGIS Extension initialized successfully. Version: %', postgis_version();
END $$;

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE TABLE IF NOT EXISTS public.teams (
    team_name text PRIMARY KEY,
    team_channel text NOT NULL,
    puzzle_solved integer NOT NULL default 0
);

CREATE TABLE IF NOT EXISTS public.players (
    discord_id text PRIMARY KEY,
    player_name text NOT NULL,
    team_name text NOT NULL REFERENCES public.teams ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.puzzles (
    puzzle_id text PRIMARY KEY,
    puzzle_name text NOT NULL,
    puzzle_answer text NOT NULL,
    puzzle_author text NOT NULL,
    uni text NOT NULL
);

CREATE TABLE IF NOT EXISTS public.submissions (
    puzzle_id text NOT NULL REFERENCES public.puzzles ON DELETE CASCADE,    
    team_name text NOT NULL REFERENCES public.teams ON DELETE CASCADE,
    submission_time timestamptz NOT NULL,
    submission_answer text NOT NULL,
    submission_is_correct boolean NOT NULL
);

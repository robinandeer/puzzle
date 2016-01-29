drop table if exists cases;
create table cases (
    id                integer primary key autoincrement,
    case_id           text not null,
    name              text not null,
    variant_source    text,
    pedigree          text
);

drop table if exists individuals;
create table individuals (
    id                integer primary key autoincrement,
    ind_id            text not null,
    case_id           text not null,
    mother            text,
    father            text,
    sex               text,
    phenotype         text,
    ind_index         integer,
    variant_source    text,
    bam_path          text
);